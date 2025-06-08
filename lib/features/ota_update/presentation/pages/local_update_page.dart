// ignore_for_file: deprecated_member_use

import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'package:path/path.dart' as p;
import 'package:google_fonts/google_fonts.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:lokasync/presentation/widgets/bottom_navbar.dart';
import 'package:lokasync/utils/mqtt_service.dart';
import 'package:typed_data/typed_data.dart'; // For Uint8Buffer
import 'package:mqtt_client/mqtt_client.dart'; // For MqttQos

class OTALogEntry {
  final DateTime timestamp;
  final String nodeCodename;
  final String firmwareVersionOrigin;
  final String message;
  final Map<String, dynamic> data;

  OTALogEntry({
    required this.timestamp,
    required this.nodeCodename,
    required this.firmwareVersionOrigin,
    required this.message,
    required this.data,
  });

  Map<String, dynamic> toJson() => {
        'timestamp': timestamp.toIso8601String(),
        'type': 'ap-ota-log',
        'message': message,
        'node_codename': nodeCodename,
        'firmware_version-origin': firmwareVersionOrigin,
        'data': data,
      };

  static OTALogEntry fromJson(Map<String, dynamic> json) => OTALogEntry(
        timestamp: DateTime.parse(json['timestamp']),
        nodeCodename: json['node_codename'],
        firmwareVersionOrigin: json['firmware_version-origin'],
        message: json['message'],
        data: Map<String, dynamic>.from(json['data']),
      );
}

class OTALogStorage {
  static const _key = 'otalog_history';

  static Future<List<OTALogEntry>> loadLogs() async {
    final prefs = await SharedPreferences.getInstance();
    final list = prefs.getStringList(_key) ?? [];
    return list.map((e) => OTALogEntry.fromJson(jsonDecode(e))).toList();
  }

  static Future<void> addLog(OTALogEntry entry) async {
    final prefs = await SharedPreferences.getInstance();
    final logs = await loadLogs();
    logs.insert(0, entry); // newest first
    await prefs.setStringList(_key, logs.map((e) => jsonEncode(e.toJson())).toList());
  }
}

class OTAUpdatePage extends StatefulWidget {
  const OTAUpdatePage({super.key});

  @override
  State<OTAUpdatePage> createState() => _OTAUpdatePageState();
}

class _OTAUpdatePageState extends State<OTAUpdatePage> {
  File? _firmwareFile;
  String? _fileName;
  String? _firmwareVersionNew;
  String _log = '';
  bool _isUploading = false;
  double _progress = 0.0;
  int? _firmwareSize;
  double? _uploadSpeed;
  double? _uploadTime;
  final _ipController = TextEditingController(text: "192.168.19.63");
  final _pwController = TextEditingController();

  Future<void> _pickFirmware() async {
    setState(() {
      _log = '';
      _progress = 0.0;
      _firmwareSize = null;
      _uploadSpeed = null;
      _uploadTime = null;
    });

    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['bin'],
    );

    if (result != null && result.files.single.path != null) {
      setState(() {
        _firmwareFile = File(result.files.single.path!);
        _fileName = p.basename(result.files.single.path!);
        _firmwareVersionNew = p.basenameWithoutExtension(result.files.single.path!);
      });
    }
  }

  String _parseESP32Field(String body, String field) {
    final reg = RegExp('$field\\s:?\\s([\\d.]+)');
    final match = reg.firstMatch(body);
    return match != null ? match.group(1)! : '-';
  }

  String _parseFirmwareVersionOrigin(String body) {
    final reg = RegExp(r'Firmware Origin: v([^\n]+)');
    final match = reg.firstMatch(body);
    return match != null ? match.group(1)!.trim() : '-';
  }

  String _parseCodename(String body) {
    final reg = RegExp(r'^([^\s]+) - Rebooting', multiLine: true);
    final match = reg.firstMatch(body);
    return match != null ? match.group(1)!.trim() : '-';
  }

  Future<void> _uploadFirmware() async {
    if (_firmwareFile == null || _ipController.text.isEmpty || _pwController.text.isEmpty) {
      setState(() {
        _log = "Please select a firmware file, enter IP and password.";
      });
      return;
    }

    setState(() {
      _isUploading = true;
      _log = "Connecting to ESP32 at ${_ipController.text} ...";
      _progress = 0.0;
    });

    final url = Uri.parse('http://${_ipController.text}/upload');
    final request = http.MultipartRequest('POST', url)
      ..fields['password'] = _pwController.text
      ..files.add(await http.MultipartFile.fromPath('update', _firmwareFile!.path));

    final stopwatch = Stopwatch()..start();

    try {
      final streamedResponse = await request.send();
      int total = _firmwareFile!.lengthSync();
      setState(() {
        _firmwareSize = total;
      });

      final response = await http.Response.fromStream(streamedResponse);
      stopwatch.stop();

      final esp32TimeRegExp = RegExp(r'Download Time  :\s([\d.]+)\sseconds', caseSensitive: false);
      double? esp32Time;
      final match = esp32TimeRegExp.firstMatch(response.body);
      if (match != null) {
        esp32Time = double.tryParse(match.group(1)!);
      }

      double? latency;
      if (esp32Time != null) {
        latency = stopwatch.elapsedMilliseconds / 1000.0 - esp32Time;
      }

      // Parse dynamic fields
      final firmwareVersionOrigin = _parseFirmwareVersionOrigin(response.body);
      final nodeCodename = _parseCodename(response.body);

      setState(() {
        _isUploading = false;
        _uploadTime = stopwatch.elapsedMilliseconds / 1000.0;
        _uploadSpeed = total / 1024.0 / (_uploadTime ?? 1);
        _log = "OTA Update Complete!\n\n"
            "Firmware Size (KBs)  : ${(_firmwareSize! / 1024).toStringAsFixed(2)} KB\n"
            "Firmware Size (Bytes): ${(_firmwareSize!).toStringAsFixed(2)} Bytes\n"
            "Upload Time (App)    : ${_uploadTime!.toStringAsFixed(2)} s\n"
            "Upload Time (ESP32)  : ${esp32Time?.toStringAsFixed(2) ?? '-'} s\n"
            "Latency              : ${latency != null ? latency.toStringAsFixed(2) : '-'} s\n"
            "Old Firmware         : $firmwareVersionOrigin\n"
            "New Firmware         : ${_firmwareVersionNew ?? '-'}\n"
            "Node Codename (SSID) : $nodeCodename\n"
            "\n\nESP32 Response   :\n${response.body}";
      });

      // Save log entry
      final logEntry = OTALogEntry(
        timestamp: DateTime.now(),
        nodeCodename: nodeCodename,
        firmwareVersionOrigin: firmwareVersionOrigin,
        message: "Local-OTA Update Complete",
        data: {
          "Firmware Size (Bytes)": _firmwareSize?.toStringAsFixed(2) ?? '-',
          "Upload Time (App)": _uploadTime?.toStringAsFixed(2) ?? '-',
          "Upload Time (ESP32)": esp32Time?.toStringAsFixed(2) ?? '-',
          "Latency": latency?.toStringAsFixed(2) ?? '-',
          "Firmware Version (New)": _firmwareVersionNew ?? '-',
          "Bytes Received": _parseESP32Field(response.body, "Bytes Received"),
          "Download Time": esp32Time?.toStringAsFixed(2) ?? '-',
          "Download Speed": _parseESP32Field(response.body, "Download Speed"),
        },
      );
      await OTALogStorage.addLog(logEntry);
    } catch (e) {
      setState(() {
        _isUploading = false;
        _log = "Error: $e";
      });
    }
  }

void _openLogHistory() {
  Navigator.push(
    context,
    MaterialPageRoute(builder: (context) => const OTALogHistoryPage()),
  );
}

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FB),
      body: SafeArea(
        child: Column(
          children: [
            // Modern Header with improved alignment
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 10,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Container(
                    decoration: BoxDecoration(
                      color: const Color(0xFF014331).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: IconButton(
                      onPressed: () => Navigator.pushReplacementNamed(context, '/home'),
                      icon: const Icon(Icons.arrow_back_ios, color: Color(0xFF014331), size: 20),
                      padding: const EdgeInsets.all(8),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Text(
                      'Local-OTA Update',
                      style: GoogleFonts.poppins(
                        fontSize: 24,
                        fontWeight: FontWeight.w700,
                        color: const Color(0xFF014331),
                        letterSpacing: -0.5,
                      ),
                    ),
                  ),
                  Container(
                    decoration: BoxDecoration(
                      color: const Color(0xFF014331).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: IconButton(
                      onPressed: _openLogHistory,
                      icon: const Icon(Icons.history_rounded, color: Color(0xFF014331), size: 24),
                      tooltip: "OTA Log History",
                      padding: const EdgeInsets.all(8),
                    ),
                  ),
                ],
              ),
            ),

            // Main Content
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Connection Section
                    Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.08),
                            blurRadius: 20,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF1976D2).withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: const Icon(
                                  Icons.settings_ethernet_rounded,
                                  color: Color(0xFF1976D2),
                                  size: 20,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Text(
                                'Connection Settings',
                                style: GoogleFonts.poppins(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w600,
                                  color: const Color(0xFF2D3748),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 20),
                          
                          // IP Address Field
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'ESP32 IP Address',
                                style: GoogleFonts.poppins(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w500,
                                  color: const Color(0xFF4A5568),
                                ),
                              ),
                              const SizedBox(height: 8),
                              TextFormField(
                                controller: _ipController,
                                enabled: !_isUploading,
                                decoration: InputDecoration(
                                  hintText: "192.168.19.63",
                                  prefixIcon: Container(
                                    margin: const EdgeInsets.all(12),
                                    padding: const EdgeInsets.all(6),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFF1976D2).withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: const Icon(Icons.wifi, color: Color(0xFF1976D2), size: 16),
                                  ),
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(12),
                                    borderSide: BorderSide(color: Colors.grey.shade300),
                                  ),
                                  enabledBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(12),
                                    borderSide: BorderSide(color: Colors.grey.shade300),
                                  ),
                                  focusedBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(12),
                                    borderSide: const BorderSide(color: Color(0xFF1976D2), width: 2),
                                  ),
                                  filled: true,
                                  fillColor: Colors.grey.shade50,
                                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                                ),
                                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                              ),
                            ],
                          ),
                          
                          const SizedBox(height: 20),
                          
                          // Password Field
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'OTA Password',
                                style: GoogleFonts.poppins(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w500,
                                  color: const Color(0xFF4A5568),
                                ),
                              ),
                              const SizedBox(height: 8),
                              TextFormField(
                                controller: _pwController,
                                enabled: !_isUploading,
                                obscureText: true,
                                decoration: InputDecoration(
                                  hintText: "Enter password",
                                  prefixIcon: Container(
                                    margin: const EdgeInsets.all(12),
                                    padding: const EdgeInsets.all(6),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFF014331).withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: const Icon(Icons.lock_rounded, color: Color(0xFF014331), size: 16),
                                  ),
                                  border: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(12),
                                    borderSide: BorderSide(color: Colors.grey.shade300),
                                  ),
                                  enabledBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(12),
                                    borderSide: BorderSide(color: Colors.grey.shade300),
                                  ),
                                  focusedBorder: OutlineInputBorder(
                                    borderRadius: BorderRadius.circular(12),
                                    borderSide: const BorderSide(color: Color(0xFF014331), width: 2),
                                  ),
                                  filled: true,
                                  fillColor: Colors.grey.shade50,
                                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 20),

                    // File Selection Section
                    Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.08),
                            blurRadius: 20,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF014331).withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: const Icon(
                                  Icons.file_present_rounded,
                                  color: Color(0xFF014331),
                                  size: 20,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Text(
                                'Firmware File',
                                style: GoogleFonts.poppins(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w600,
                                  color: const Color(0xFF2D3748),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 20),
                          
                          // File picker button and display
                          Row(
                            children: [
                              ElevatedButton.icon(
                                onPressed: _isUploading ? null : _pickFirmware,
                                icon: const Icon(Icons.folder_open_rounded, size: 18),
                                label: Text(
                                  "Select Firmware",
                                  style: GoogleFonts.poppins(fontWeight: FontWeight.w500),
                                ),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: const Color(0xFF014331),
                                  foregroundColor: Colors.white,
                                  disabledBackgroundColor: Colors.grey.shade300,
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                                  elevation: 0,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                                  decoration: BoxDecoration(
                                    color: _fileName != null ? const Color(0xFF014331).withOpacity(0.05) : Colors.grey.shade100,
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(
                                      color: _fileName != null ? const Color(0xFF014331).withOpacity(0.2) : Colors.grey.shade300,
                                    ),
                                  ),
                                  child: Row(
                                    children: [
                                      Icon(
                                        _fileName != null ? Icons.check_circle_outline : Icons.insert_drive_file_outlined,
                                        size: 16,
                                        color: _fileName != null ? const Color(0xFF014331) : Colors.grey.shade500,
                                      ),
                                      const SizedBox(width: 8),
                                      Expanded(
                                        child: Text(
                                          _fileName ?? "No file selected",
                                          style: GoogleFonts.poppins(
                                            fontSize: 13,
                                            color: _fileName != null ? const Color(0xFF014331) : Colors.grey.shade600,
                                            fontWeight: _fileName != null ? FontWeight.w500 : FontWeight.normal,
                                          ),
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 20),

                    // Upload Button
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: ElevatedButton.icon(
                        onPressed: _isUploading ? null : _uploadFirmware,
                        icon: _isUploading 
                          ? SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Colors.white.withOpacity(0.8)),
                              ),
                            )
                          : const Icon(Icons.cloud_upload_rounded, size: 20),
                        label: Text(
                          _isUploading ? "Uploading..." : "Start OTA Update",
                          style: GoogleFonts.poppins(
                            fontSize: 16,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF1976D2),
                          foregroundColor: Colors.white,
                          disabledBackgroundColor: Colors.grey.shade400,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          elevation: 0,
                          shadowColor: const Color(0xFF1976D2).withOpacity(0.3),
                        ),
                      ),
                    ),

                    // Progress indicator
                    if (_isUploading) ...[
                      const SizedBox(height: 16),
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: const Color(0xFF1976D2).withOpacity(0.2)),
                        ),
                        child: Column(
                          children: [
                            Row(
                              children: [
                                const Icon(Icons.upload, color: Color(0xFF1976D2), size: 16),
                                const SizedBox(width: 8),
                                Text(
                                  'Upload in progress...',
                                  style: GoogleFonts.poppins(
                                    fontSize: 14,
                                    fontWeight: FontWeight.w500,
                                    color: const Color(0xFF1976D2),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: LinearProgressIndicator(
                                value: _progress,
                                backgroundColor: Colors.grey.shade200,
                                valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF1976D2)),
                                minHeight: 6,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],

                    const SizedBox(height: 20),

                    // Enhanced Log Display
                    Container(
                      width: double.infinity,
                      height: 600,
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1A1A1A),
                        borderRadius: BorderRadius.circular(16),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.15),
                            blurRadius: 20,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(6),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF00D4AA).withOpacity(0.2),
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: const Icon(
                                  Icons.terminal_rounded,
                                  color: Color(0xFF00D4AA),
                                  size: 16,
                                ),
                              ),
                              const SizedBox(width: 10),
                              Text(
                                'Console Output',
                                style: GoogleFonts.poppins(
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white,
                                ),
                              ),
                              const Spacer(),
                              Container(
                                width: 8,
                                height: 8,
                                decoration: BoxDecoration(
                                  color: _isUploading ? const Color(0xFFFF6B6B) : const Color(0xFF00D4AA),
                                  shape: BoxShape.circle,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                _isUploading ? 'Active' : 'Ready',
                                style: GoogleFonts.poppins(
                                  fontSize: 12,
                                  color: Colors.white.withOpacity(0.7),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          Expanded(
                            child: Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: Colors.black.withOpacity(0.3),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(
                                  color: Colors.white.withOpacity(0.1),
                                ),
                              ),
                              child: SingleChildScrollView(
                                child: Text(
                                  _log.isEmpty ? 'Waiting for OTA update...' : _log,
                                  style: GoogleFonts.jetBrainsMono(
                                    fontSize: 12,
                                    color: _log.isEmpty ? Colors.white.withOpacity(0.5) : const Color(0xFF00D4AA),
                                    height: 1.5,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavBar(
        currentIndex: 3, // 4th tab
        onTap: (index) {
          if (index != 3) {
            if (index == 0) {
              Navigator.pushReplacementNamed(context, '/home');
            } else if (index == 1) {
              Navigator.pushReplacementNamed(context, '/monitoring');
            } else if (index == 2) {
              Navigator.pushReplacementNamed(context, '/profile');
            }
          }
        },
      ),
    );
  }
}

class OTALogHistoryPage extends StatefulWidget {
  const OTALogHistoryPage({super.key});

  @override
  State<OTALogHistoryPage> createState() => _OTALogHistoryPageState();
}

class _OTALogHistoryPageState extends State<OTALogHistoryPage> {
  List<OTALogEntry> _logs = [];

  @override
  void initState() {
    super.initState();
    _loadLogs();
  }

  Future<void> _loadLogs() async {
    final logs = await OTALogStorage.loadLogs();
    setState(() => _logs = logs);
  }

  void _uploadLog(OTALogEntry entry) async {
    final payload = jsonEncode(entry.toJson());
    final buffer = Uint8Buffer()..addAll(utf8.encode(payload));
    MQTTService().client.publishMessage(
      'LokaSync/LocalLog/LocalOTAUpdate',
      MqttQos.atLeastOnce,
      buffer,
    );
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Log uploaded to MQTT!')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8F9FB),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leading: Container(
          margin: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: const Color(0xFF014331).withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: IconButton(
            onPressed: () => Navigator.pop(context),
            icon: const Icon(Icons.arrow_back_ios, color: Color(0xFF014331), size: 18),
          ),
        ),
        title: Text(
          'OTA Update History',
          style: GoogleFonts.poppins(
            fontSize: 20,
            fontWeight: FontWeight.w600,
            color: const Color(0xFF014331),
          ),
        ),
        centerTitle: true,
      ),
      body: _logs.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.all(32),
                    decoration: BoxDecoration(
                      color: Colors.grey.shade100,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.history_rounded,
                      size: 64,
                      color: Colors.grey.shade400,
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text(
                    'No OTA logs yet',
                    style: GoogleFonts.poppins(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Your OTA update history will appear here',
                    style: GoogleFonts.poppins(
                      fontSize: 14,
                      color: Colors.grey.shade500,
                    ),
                  ),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _logs.length,
              itemBuilder: (context, i) {
                final log = _logs[i];
                return Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.08),
                        blurRadius: 10,
                        offset: const Offset(0, 2),
                      ),
                    ],
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(16),
                    leading: Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF00D4AA).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Icon(
                        Icons.system_update_rounded,
                        color: Color(0xFF00D4AA),
                        size: 24,
                      ),
                    ),
                    title: Text(
                      log.message,
                      style: GoogleFonts.poppins(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: const Color(0xFF2D3748),
                      ),
                    ),
                    subtitle: Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.access_time, size: 14, color: Colors.grey.shade500),
                              const SizedBox(width: 4),
                              Text(
                                '${log.timestamp.day}/${log.timestamp.month}/${log.timestamp.year} ${log.timestamp.hour}:${log.timestamp.minute.toString().padLeft(2, '0')}',
                                style: GoogleFonts.poppins(
                                  fontSize: 12,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              Icon(Icons.router, size: 14, color: Colors.grey.shade500),
                              const SizedBox(width: 4),
                              Text(
                                log.nodeCodename,
                                style: GoogleFonts.poppins(
                                  fontSize: 12,
                                  color: Colors.grey.shade600,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    trailing: Container(
                      decoration: BoxDecoration(
                        color: const Color(0xFF1976D2).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: IconButton(
                        icon: const Icon(
                          Icons.cloud_upload_rounded,
                          color: Color(0xFF1976D2),
                          size: 20,
                        ),
                        onPressed: () => _uploadLog(log),
                        tooltip: 'Upload to MQTT',
                      ),
                    ),
                    onTap: () {
                      showDialog(
                        context: context,
                        builder: (context) => AlertDialog(
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(16),
                          ),
                          title: Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF00D4AA).withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: const Icon(
                                  Icons.info_outline,
                                  color: Color(0xFF00D4AA),
                                  size: 20,
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(
                                  log.message,
                                  style: GoogleFonts.poppins(
                                    fontSize: 18,
                                    fontWeight: FontWeight.w600,
                                    color: const Color(0xFF2D3748),
                                  ),
                                ),
                              ),
                            ],
                          ),
                          content: Container(
                            width: double.maxFinite,
                            constraints: const BoxConstraints(maxHeight: 400),
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: const Color(0xFF1A1A1A),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: SingleChildScrollView(
                              child: Text(
                                const JsonEncoder.withIndent('  ').convert(log.toJson()),
                                style: GoogleFonts.jetBrainsMono(
                                  fontSize: 12,
                                  color: const Color(0xFF00D4AA),
                                  height: 1.4,
                                ),
                              ),
                            ),
                          ),
                          actions: [
                            TextButton(
                              onPressed: () => Navigator.pop(context),
                              child: Text(
                                'Close',
                                style: GoogleFonts.poppins(
                                  fontWeight: FontWeight.w500,
                                  color: const Color(0xFF1976D2),
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                );
              },
            ),
    );
  }
}