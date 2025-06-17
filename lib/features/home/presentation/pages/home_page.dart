import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lokasync/presentation/widgets/bottom_navbar.dart';
import 'package:mqtt5_client/mqtt5_client.dart';
import 'package:lokasync/utils/mqtt_service.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:typed_data/typed_data.dart';

class Home extends StatefulWidget {
  const Home({super.key});

  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  // Firmware version control state
  List<Map<String, dynamic>> _nodes = [];
  bool _loadingNodes = false;
  int _nodePage = 1;
  int _nodePageSize = 10;
  int _nodeTotal = 0;

  // OTA log state
  List<Map<String, dynamic>> _logs = [];
  bool _loadingLogs = false;
  int _logPage = 1;
  int _logPageSize = 10;
  int _logTotal = 0;

  int currentIndex = 0;
  String? _idToken;
  String _activeTab = 'version_control';

  // Version selection and firmware URL cache
  final Map<String, List<String>> _nodeVersions = {};
  final Map<String, String> _selectedVersion = {};
  final Map<String, String> _firmwareUrls = {};

  @override
  void initState() {
    super.initState();
    _getIdTokenAndFetch();
  }

  Future<void> _getIdTokenAndFetch() async {
    setState(() {
      _loadingNodes = true;
      _loadingLogs = true;
    });
    try {
      final user = FirebaseAuth.instance.currentUser;
      final token = await user?.getIdToken();
      setState(() {
        _idToken = token;
      });
      await Future.wait([_fetchNodes(), _fetchLogs()]);
    } catch (e) {
      setState(() {
        _loadingNodes = false;
        _loadingLogs = false;
      });
    }
  }

  Future<void> _fetchNodes() async {
    if (_idToken == null) return;
    setState(() => _loadingNodes = true);
    final uri = Uri.https('lokasync.tech', '/api/v1/node/', {
      'page': _nodePage.toString(),
      'page_size': _nodePageSize.toString(),
    });
    final res = await http.get(
      uri,
      headers: {'Authorization': 'Bearer $_idToken'},
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      final nodes = List<Map<String, dynamic>>.from(data['data'] ?? []);
      _nodes = nodes;
      _nodeTotal = data['total_data'] ?? nodes.length;
      // Fetch all versions for all nodes and wait for all to complete
      await Future.wait(nodes.map((node) async {
        final codename = node['node_codename'];
        if (codename != null && !_nodeVersions.containsKey(codename)) {
          await _fetchNodeVersions(codename);
        }
      }));
      setState(() {
        _loadingNodes = false;
      });
    } else {
      setState(() => _loadingNodes = false);
    }
  }

  Future<void> _fetchLogs() async {
    if (_idToken == null) return;
    setState(() => _loadingLogs = true);
    final uri = Uri.https('lokasync.tech', '/api/v1/log/', {
      'page': _logPage.toString(),
      'page_size': _logPageSize.toString(),
    });
    final res = await http.get(
      uri,
      headers: {'Authorization': 'Bearer $_idToken'},
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      setState(() {
        _logs = List<Map<String, dynamic>>.from(data['data'] ?? []);
        _logTotal = data['total_data'] ?? _logs.length;
        _loadingLogs = false;
      });
    } else {
      setState(() => _loadingLogs = false);
    }
  }

  // Fetch all versions for a node
  Future<void> _fetchNodeVersions(String nodeCodename) async {
    if (_nodeVersions.containsKey(nodeCodename)) return;
    final uri = Uri.https('lokasync.tech', '/api/v1/node/version/$nodeCodename');
    final res = await http.get(uri, headers: {'Authorization': 'Bearer $_idToken'});
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      final versions = List<String>.from(data['data'] ?? []);
      setState(() {
        _nodeVersions[nodeCodename] = versions;
        // Default to latest version if available
        if (versions.isNotEmpty) {
          _selectedVersion[nodeCodename] = versions.first;
        }
      });
    }
  }

  // Fetch firmware detail for a node/version
  Future<void> _fetchFirmwareDetail(String nodeCodename, String version) async {
    if (version.isEmpty) return;
    final uri = Uri.https('lokasync.tech', '/api/v1/node/detail/$nodeCodename', {'firmware_version': version});
    final res = await http.get(uri, headers: {'Authorization': 'Bearer $_idToken'});
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      setState(() {
        _firmwareUrls['$nodeCodename|$version'] = data['data']?['firmware_url'] ?? '';
      });
    }
  }

  // Download firmware file using direct link and url_launcher
  Future<void> _downloadFirmware(String nodeCodename, String version) async {
    if (version.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No version selected')),
      );
      return;
    }
    // Get firmware detail to obtain the direct download URL
    final uri = Uri.https('lokasync.tech', '/api/v1/node/detail/$nodeCodename', {
      'firmware_version': version,
    });
    final res = await http.get(uri, headers: {'Authorization': 'Bearer $_idToken'});
    
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      final url = data['data']?['firmware_url'];
      if (url != null && url is String && url.isNotEmpty) {
        // Open the direct download link in the browser
        await launchUrl(Uri.parse(url));
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Firmware URL not found')),
        );
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to get firmware URL')),
      );
    }
  }

  // Publish MQTT payload for OTA update
  Future<void> _publishOtaPayload(String nodeCodename, String version) async {
    await _fetchFirmwareDetail(nodeCodename, version);
    final url = _firmwareUrls['$nodeCodename|$version'];
    if (url == null || url.isEmpty) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Firmware URL not found')));
      return;
    }
    final payload = {
      "node_codename": nodeCodename,
      "firmware_url": url,
      "firmware_version": version,
      "session_id": _generateSessionId(),
    };
    try {
      final buffer = Uint8Buffer()..addAll(utf8.encode(jsonEncode(payload)));
      MQTTService().client.publishMessage(
        'LokaSync/CloudOTA/FirmwareUpdate',
        MqttQos.atLeastOnce,
        buffer,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('OTA payload published via MQTT!')));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('MQTT publish failed: $e')));
    }
  }

  String _generateSessionId() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    String rand() {
      final r = List.generate(5, (_) => chars[(DateTime.now().millisecondsSinceEpoch + _randomInt()) % chars.length]).join();
      final n = List.generate(5, (_) => (_randomInt() % 10).toString()).join();
      return r + n;
    }
    return rand();
  }

  int _randomInt() => DateTime.now().microsecondsSinceEpoch % 100;

  void _onItemTapped(int index) {
    if (index == currentIndex) return;
    if (index == 1) {
      Navigator.pushReplacementNamed(context, '/monitoring');
    } else if (index == 2) {
      Navigator.pushReplacementNamed(context, '/profile');
    } else if (index == 3) {
      Navigator.pushReplacementNamed(context, '/local-update');
    }
  }

  String _getFirstName() {
    final user = FirebaseAuth.instance.currentUser;
    if (user != null && user.displayName != null && user.displayName!.isNotEmpty) {
      return user.displayName!.split(' ')[0];
    }
    return 'User';
  }

  Widget _buildStatCard(String title, int value, IconData icon, Color color) {
  return GestureDetector(
    onTap: () {
      if (title.contains('Version Control')) {
        setState(() => _activeTab = 'version_control');
      } else if (title.contains('Update Log')) {
        setState(() => _activeTab = 'ota_logs');
      }
    },
    child: Container(
      width: 150,
      height: 120,
      margin: const EdgeInsets.only(right: 12),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            color,
            color.withOpacity(0.7),
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.3),
            spreadRadius: 1,
            blurRadius: 6,
            offset: const Offset(0, 3),
          ),
        ],
      ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                color: Colors.white,
                size: 28,
              ),
              const SizedBox(height: 8),
              Text(
                value.toString(),
                style: GoogleFonts.poppins(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                title,
                style: GoogleFonts.poppins(
                  fontSize: 10,
                  color: Colors.white,
                  fontWeight: FontWeight.w500,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildVersionControlContent() {
  if (_loadingNodes) {
    return const Center(
      child: CircularProgressIndicator(
        color: Color(0xFF014331),
      ),
    );
  }

  return Column(
    children: [
      Expanded(
        child: ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: _nodes.length,
          itemBuilder: (context, index) {
            final node = _nodes[index];
            return _buildNodeCard(node);
          },
        ),
      ),
      // Pagination stays at the bottom of the container
      Container(
        color: Colors.white,
        child: _buildPagination(
          page: _nodePage,
          pageSize: _nodePageSize,
          total: _nodeTotal,
          onPageChange: (p) {
            setState(() => _nodePage = p);
            _fetchNodes();
          },
          onPageSizeChange: (s) {
            setState(() => _nodePageSize = s);
            _fetchNodes();
          },
        ),
      ),
    ],
  );
}

  Widget _buildOtaLogsContent() {
    if (_loadingLogs) {
      return const Center(
        child: CircularProgressIndicator(
          color: Color(0xFF014331),
        ),
      );
    }

    return Column(
      children: [
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: _logs.length,
            itemBuilder: (context, index) {
              final log = _logs[index];
              return _buildLogCard(log);
            },
          ),
        ),
        Container(
          color: Colors.white,
          child: _buildPagination(
            page: _logPage,
            pageSize: _logPageSize,
            total: _logTotal,
            onPageChange: (p) {
              setState(() => _logPage = p);
              _fetchLogs();
            },
            onPageSizeChange: (s) {
              setState(() => _logPageSize = s);
              _fetchLogs();
            },
          ),
        ),
      ],
    );
  }

  Widget _buildNodeCard(Map<String, dynamic> node) {
    final nodeCodename = node['node_codename'] ?? '';
    final versions = _nodeVersions[nodeCodename] ?? [];
    final items = versions.isNotEmpty
        ? versions
        : [node['firmware_version']?.toString() ?? '-'];
    final selectedVersion = _selectedVersion[nodeCodename] ?? 
        (versions.isNotEmpty ? versions.first : null);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.shade200,
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: const Color(0xFF014331).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.developer_board,
                    color: Color(0xFF014331),
                    size: 24,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        node['node_location']?.toString() ?? 'Unknown Location',
                        style: GoogleFonts.poppins(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: const Color(0xFF014331),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${node['node_type']?.toString() ?? '-'} • ID: ${node['node_id']?.toString() ?? '-'}',
                        style: GoogleFonts.poppins(
                          fontSize: 12,
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              node['description']?.toString() ?? 'No description available',
              style: GoogleFonts.poppins(
                fontSize: 14,
                color: Colors.black87,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Firmware Version',
                        style: GoogleFonts.poppins(
                          fontSize: 12,
                          color: Colors.grey.shade600,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.grey.shade300),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: DropdownButton<String>(
                          value: selectedVersion,
                          isExpanded: true,
                          underline: Container(),
                          items: items
                              .where((v) => v.isNotEmpty && v != '-')
                              .map((v) => DropdownMenuItem(
                                    value: v,
                                    child: Text(
                                      v,
                                      style: GoogleFonts.poppins(fontSize: 12),
                                    ),
                                  ))
                              .toList(),
                          onChanged: (v) {
                            if (v == null) return;
                            setState(() {
                              _selectedVersion[nodeCodename] = v;
                            });
                          },
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Column(
                  children: [
                    ElevatedButton.icon(
                      onPressed: () => _publishOtaPayload(
                        nodeCodename,
                        _selectedVersion[nodeCodename] ?? node['firmware_version'] ?? '',
                      ),
                      icon: const Icon(Icons.cloud_upload, size: 16),
                      label: Text(
                        'Upload OTA',
                        style: GoogleFonts.poppins(fontSize: 12),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF014331),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    OutlinedButton.icon(
                      onPressed: () => _downloadFirmware(
                        nodeCodename,
                        _selectedVersion[nodeCodename] ?? node['firmware_version'] ?? '',
                      ),
                      icon: const Icon(Icons.download, size: 16),
                      label: Text(
                        'Download',
                        style: GoogleFonts.poppins(fontSize: 12),
                      ),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF014331),
                        side: const BorderSide(color: Color(0xFF014331)),
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              'Last Updated: ${_formatDate(node['latest_updated'])}',
              style: GoogleFonts.poppins(
                fontSize: 12,
                color: Colors.grey.shade500,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLogCard(Map<String, dynamic> log) {
    final bool isSuccess = log['flash_status']?.toString().toLowerCase() == 'success';
    final Color statusColor = isSuccess ? Colors.green : Colors.red;
    final IconData statusIcon = isSuccess ? Icons.check_circle : Icons.error;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.shade200,
            spreadRadius: 1,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: statusColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                statusIcon,
                color: statusColor,
                size: 24,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    log['node_codename']?.toString() ?? 'Unknown Node',
                    style: GoogleFonts.poppins(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: const Color(0xFF014331),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'MAC: ${log['node_mac']?.toString() ?? '-'}',
                    style: GoogleFonts.poppins(
                      fontSize: 10,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Text(
                        'Version: ${log['firmware_version']?.toString() ?? '-'}',
                        style: GoogleFonts.poppins(
                          fontSize: 10,
                          color: Colors.black87,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Text(
                        'Size: ${log['firmware_size_kb'] ?? '-'} KB',
                        style: GoogleFonts.poppins(
                          fontSize: 10,
                          color: Colors.black87,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      log['flash_status']?.toString() ?? 'Unknown',
                      style: GoogleFonts.poppins(
                        fontSize: 10,
                        color: statusColor,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPagination({
    required int page,
    required int pageSize,
    required int total,
    required void Function(int) onPageChange,
    required void Function(int) onPageSizeChange,
  }) {
    final totalPages = (total / pageSize).ceil();
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(top: BorderSide(color: Colors.grey.shade200)),
      ),
      child: Row(
        children: [
          Text(
            'Page $page of $totalPages',
            style: GoogleFonts.poppins(
              fontSize: 14,
              color: Colors.grey.shade700,
            ),
          ),
          IconButton(
            icon: const Icon(Icons.chevron_left),
            onPressed: page > 1 ? () => onPageChange(page - 1) : null,
            color: const Color(0xFF014331),
          ),
          IconButton(
            icon: const Icon(Icons.chevron_right),
            onPressed: page < totalPages ? () => onPageChange(page + 1) : null,
            color: const Color(0xFF014331),
          ),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey.shade300),
              borderRadius: BorderRadius.circular(8),
            ),
            child: DropdownButton<int>(
              value: pageSize,
              underline: Container(),
              items: [10, 25, 50, 100]
                  .map((s) => DropdownMenuItem(
                        value: s,
                        child: Text(
                          '$s',
                          style: GoogleFonts.poppins(fontSize: 14),
                        ),
                      ))
                  .toList(),
              onChanged: (s) => onPageSizeChange(s!),
            ),
          ),
        ],
      ),
    );
  }

  String _formatDate(dynamic date) {
    if (date == null) return '-';
    final dt = DateTime.tryParse(date.toString());
    if (dt == null) return '-';
    return '${dt.day}/${dt.month}/${dt.year} ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7F9),
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with user greeting and profile icon
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Hi, ${_getFirstName()}',
                        style: GoogleFonts.poppins(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: const Color(0xFF014331),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Manage your IoT OTA updates',
                        style: GoogleFonts.poppins(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                  GestureDetector(
                    onTap: () {
                      Navigator.pushReplacementNamed(context, '/profile');
                    },
                    child: CircleAvatar(
                      backgroundColor: const Color(0xFF014331),
                      radius: 24,
                      child: const Icon(
                        Icons.person,
                        color: Colors.white,
                        size: 28,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Tab selector cards
            SizedBox(
              height: 130,
              child: ListView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                children: [
                  _buildStatCard('Cloud-OTA Version Control', _nodeTotal, Icons.cloud_sync, const Color(0xFF014331)),
                  _buildStatCard('Cloud-OTA Update Log', _logTotal, Icons.history, const Color(0xFF1976D2)),
                  _buildStatCard('Local-OTA Update Log', 0, Icons.smartphone, const Color(0xFFBF04)),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Content based on active tab
            Expanded(
              child: _activeTab == 'version_control'
                  ? _buildVersionControlContent()
                  : _buildOtaLogsContent(),
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavBar(
        currentIndex: currentIndex,
        onTap: _onItemTapped,
      ),
    );
  }
}