import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:math';
import 'package:fl_chart/fl_chart.dart';
import 'package:lokasync/presentation/widgets/bottom_navbar.dart';
import 'package:lokasync/utils/sensor_data_holder.dart';

// Sensor metadata for icon/unit/color mapping
const sensorMeta = {
  'temperature': {
    'name': 'Suhu',
    'unit': '°C',
    'icon': Icons.thermostat,
    'color': Color(0xFF2E7D32),
  },
  'humidity': {
    'name': 'Kelembaban',
    'unit': '%',
    'icon': Icons.water_drop,
    'color': Color(0xFF1976D2),
  },
  'PPM': {
    'name': 'TDS',
    'unit': 'PPM',
    'icon': Icons.opacity,
    'color': Color(0xFF7B1FA2),
  },
  // Add more sensor types here as needed
};

class SensorData {
  final String id;
  final String name;
  final double value;
  final String unit;
  final IconData icon;
  final Color color;
  final List<double> history;

  SensorData({
    required this.id,
    required this.name,
    required this.value,
    required this.unit,
    required this.icon,
    required this.color,
    required this.history,
  });

  SensorData copyWith({double? value, List<double>? history}) {
    return SensorData(
      id: id,
      name: name,
      value: value ?? this.value,
      unit: unit,
      icon: icon,
      color: color,
      history: history ?? this.history,
    );
  }
}

class MonitoringNode {
  final String id;
  final String name;
  final Map<String, SensorData> sensors;

  MonitoringNode({
    required this.id,
    required this.name,
    required this.sensors,
  });

  MonitoringNode copyWith({Map<String, SensorData>? sensors}) {
    return MonitoringNode(
      id: id,
      name: name,
      sensors: sensors ?? this.sensors,
    );
  }
}

class Monitoring extends StatefulWidget {
  const Monitoring({super.key});

  @override
  State<Monitoring> createState() => _MonitoringState();
}

Map<String, String> parseCodename(String codename) {
  final parts = codename.split('_');
  return {
    'location': parts[0].toUpperCase(),
    'type': parts.length > 1 ? parts[1].toUpperCase() : '',
    'id': parts.length > 2 ? parts[2].toUpperCase() : '',
  };
}

class _MonitoringState extends State<Monitoring> {
  late final SensorDataHolder _dataHolder;
  String? _selectedNodeId;
  String? _selectedSensorId;
  final bool _isLoading = false;
  final int _currentIndex = 1;

  @override
  void initState() {
    super.initState();
    _dataHolder = SensorDataHolder();
    _dataHolder.addListener(_onDataUpdate);
    _autoSelectFirstNodeAndSensor();
  }

  void _onDataUpdate() {
    setState(() {
      _autoSelectFirstNodeAndSensor();
    });
  }

  void _autoSelectFirstNodeAndSensor() {
    // Auto-select first node and sensor if not already selected
    if (_dataHolder.nodes.isNotEmpty) {
      _selectedNodeId ??= _dataHolder.nodes.values.first.id;
      final sensors = _dataHolder.nodes[_selectedNodeId!]?.sensors ?? {};
      _selectedSensorId ??= sensors.isNotEmpty ? sensors.keys.first : null;
    }
  }

  @override
  void dispose() {
    _dataHolder.removeListener(_onDataUpdate);
    super.dispose();
  }

  MonitoringNode? get _selectedNode =>
      _selectedNodeId != null ? _dataHolder.nodes[_selectedNodeId!] : null;

  SensorData? get _selectedSensor =>
      _selectedSensorId != null ? _selectedNode?.sensors[_selectedSensorId!] : null;

@override
Widget build(BuildContext context) {
  final node = _selectedNode;
  final sensors = node?.sensors.values.toList() ?? [];
  return Scaffold(
    backgroundColor: const Color(0xFFF5F7F9),
    body: SafeArea(
      child: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF014331)))
          : Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Header (no back arrow)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 16.0),
                    child: Row(
                      children: [
                        Text(
                          'Monitoring Page',
                          style: GoogleFonts.poppins(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: const Color(0xFF014331),
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Node selector
                  Padding(
                    padding: const EdgeInsets.only(bottom: 16.0),
                    child: _buildNodeDropdown(),
                  ),
                  // Sensor cards
                  SizedBox(
                    height: 110,
                    child: sensors.isEmpty
                        ? const Center(child: Text('No node available'))
                        : ListView.builder(
                            scrollDirection: Axis.horizontal,
                            itemCount: sensors.length,
                            itemBuilder: (context, index) {
                              final sensor = sensors[index];
                              return _buildSensorCard(sensor);
                            },
                          ),
                  ),
                  const SizedBox(height: 24),
                  // Sensor visualization
                  if (_selectedSensor != null)
                    Expanded(
                      child: SingleChildScrollView(
                        physics: const BouncingScrollPhysics(),
                        child: Padding(
                          padding: const EdgeInsets.only(bottom: 16.0),
                          child: _buildSensorVisualization(_selectedSensor!),
                        ),
                      ),
                    ),
                ],
              ),
            ),
    ),
    bottomNavigationBar: BottomNavBar(
      currentIndex: _currentIndex,
      onTap: (index) {
        if (index != _currentIndex) {
          if (index == 0) {
            Navigator.pushReplacementNamed(context, '/home');
          } else if (index == 1) {
            Navigator.pushReplacementNamed(context, '/monitoring');
          } else if (index == 2) {
            Navigator.pushReplacementNamed(context, '/local-update');
          } else if (index == 3) {
            Navigator.pushReplacementNamed(context, '/profile');
          }
        }
      },
    ),
  );
}

Widget _buildNodeDropdown() {
  // Group nodes by location and type
  final nodes = _dataHolder.nodes.values.toList();
  final Map<String, Map<String, List<MonitoringNode>>> categorized = {};
  
  for (final node in nodes) {
    final parsed = parseCodename(node.id);
    final loc = parsed['location']!;
    final type = parsed['type']!;
    categorized.putIfAbsent(loc, () => {});
    categorized[loc]!.putIfAbsent(type, () => []);
    categorized[loc]![type]!.add(node);
  }
  
  // Build dropdowns
  final locations = categorized.keys.toList()..sort();
  String? selectedLocation = _selectedNodeId != null
      ? parseCodename(_selectedNodeId!)['location']
      : (locations.isNotEmpty ? locations.first : null);
      
  final types = (selectedLocation != null && categorized[selectedLocation] != null)
      ? (categorized[selectedLocation]!.keys.toList()..sort())
      : <String>[];
      
  String? selectedType = _selectedNodeId != null
      ? parseCodename(_selectedNodeId!)['type']
      : (types.isNotEmpty ? types.first : null);
      
  final ids = (selectedLocation != null && selectedType != null && categorized[selectedLocation] != null && categorized[selectedLocation]![selectedType] != null)
      ? categorized[selectedLocation]![selectedType]!
          .map((n) => parseCodename(n.id)['id']!)
          .toList()
      : <String>[];
      
  String? selectedId = _selectedNodeId != null
      ? parseCodename(_selectedNodeId!)['id']
      : (ids.isNotEmpty ? ids.first : null);

  return Container(
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(20),
      boxShadow: [
        BoxShadow(
          color: Colors.grey.shade200,
          blurRadius: 8,
          spreadRadius: 2,
          offset: const Offset(0, 4),
        ),
      ],
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Location Dropdown (Full width at top)
        Text(
          'Node Location',
          style: GoogleFonts.poppins(
            fontSize: 12,
            fontWeight: FontWeight.w500,
            color: Colors.grey.shade600,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey.shade300),
            borderRadius: BorderRadius.circular(12),
            color: Colors.grey.shade50,
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value: selectedLocation,
              isExpanded: true,
              hint: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  'Choose Location',
                  style: GoogleFonts.poppins(
                    color: Colors.grey.shade500,
                    fontSize: 14,
                  ),
                ),
              ),
              icon: Padding(
                padding: const EdgeInsets.only(right: 12),
                child: Icon(
                  Icons.keyboard_arrow_down_rounded,
                  color: Colors.grey.shade600,
                  size: 24,
                ),
              ),
              style: GoogleFonts.poppins(
                color: const Color(0xFF014331),
                fontSize: 14,
                fontWeight: FontWeight.w500,
              ),
              dropdownColor: Colors.white,
              borderRadius: BorderRadius.circular(12),
              elevation: 8,
              onChanged: (loc) {
                setState(() {
                  if (loc != null && categorized[loc] != null && categorized[loc]!.isNotEmpty) {
                    final firstType = categorized[loc]!.keys.first;
                    final firstNode = categorized[loc]![firstType]!.first;
                    _selectedNodeId = firstNode.id;
                    final sensors = firstNode.sensors;
                    _selectedSensorId = sensors.isNotEmpty ? sensors.keys.first : null;
                  }
                });
              },
              items: locations.map((loc) => DropdownMenuItem(
                value: loc,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  child: Text(
                    loc.replaceAll('-', ' - '),
                    style: GoogleFonts.poppins(
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              )).toList(),
            ),
          ),
        ),
        
        const SizedBox(height: 20),
        
        // Type and ID Dropdowns (Side by side at bottom)
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Type Dropdown (Larger - 2/3 width)
            Expanded(
              flex: 2,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Node Type',
                    style: GoogleFonts.poppins(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey.shade300),
                      borderRadius: BorderRadius.circular(12),
                      color: Colors.grey.shade50,
                    ),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: selectedType,
                        isExpanded: true,
                        hint: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 12),
                          child: Text(
                            'Type',
                            style: GoogleFonts.poppins(
                              color: Colors.grey.shade500,
                              fontSize: 13,
                            ),
                          ),
                        ),
                        icon: Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: Icon(
                            Icons.keyboard_arrow_down_rounded,
                            color: Colors.grey.shade600,
                            size: 20,
                          ),
                        ),
                        style: GoogleFonts.poppins(
                          color: const Color(0xFF014331),
                          fontSize: 13,
                          fontWeight: FontWeight.w500,
                        ),
                        dropdownColor: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        elevation: 8,
                        onChanged: (type) {
                          setState(() {
                            if (selectedLocation != null &&
                                type != null &&
                                categorized[selectedLocation] != null &&
                                categorized[selectedLocation]![type] != null &&
                                categorized[selectedLocation]![type]!.isNotEmpty) {
                              final firstNode = categorized[selectedLocation]![type]!.first;
                              _selectedNodeId = firstNode.id;
                              final sensors = firstNode.sensors;
                              _selectedSensorId = sensors.isNotEmpty ? sensors.keys.first : null;
                            }
                          });
                        },
                        items: types.map((type) => DropdownMenuItem(
                          value: type,
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            child: Text(
                              type,
                              style: GoogleFonts.poppins(
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        )).toList(),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(width: 12),
            
            // ID Dropdown (Smaller - 1/3 width)
            Expanded(
              flex: 1,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'ID',
                    style: GoogleFonts.poppins(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey.shade300),
                      borderRadius: BorderRadius.circular(12),
                      color: Colors.grey.shade50,
                    ),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: selectedId,
                        isExpanded: true,
                        hint: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 8),
                          child: Text(
                            'ID',
                            style: GoogleFonts.poppins(
                              color: Colors.grey.shade500,
                              fontSize: 13,
                            ),
                          ),
                        ),
                        icon: Padding(
                          padding: const EdgeInsets.only(right: 6),
                          child: Icon(
                            Icons.keyboard_arrow_down_rounded,
                            color: Colors.grey.shade600,
                            size: 18,
                          ),
                        ),
                        style: GoogleFonts.poppins(
                          color: const Color(0xFF014331),
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                        ),
                        dropdownColor: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        elevation: 8,
                        onChanged: (id) {
                          setState(() {
                            if (selectedLocation != null &&
                                selectedType != null &&
                                id != null &&
                                categorized[selectedLocation] != null &&
                                categorized[selectedLocation]![selectedType] != null) {
                              try {
                                final node = categorized[selectedLocation]![selectedType]!
                                    .firstWhere((n) => parseCodename(n.id)['id'] == id);
                                _selectedNodeId = node.id;
                                final sensors = node.sensors;
                                _selectedSensorId = sensors.isNotEmpty ? sensors.keys.first : null;
                              } catch (e) {
                                // Handle case where node is not found
                                debugPrint('Node not found: $e');
                              }
                            }
                          });
                        },
                        items: ids.map((id) => DropdownMenuItem(
                          value: id,
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                            child: Text(
                              id,
                              style: GoogleFonts.poppins(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        )).toList(),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ],
    ),
  );
}

  Widget _buildSensorCard(SensorData sensor) {
    final bool isSelected = _selectedSensorId == sensor.id;
    return GestureDetector(
      onTap: () {
        setState(() => _selectedSensorId = sensor.id);
      },
      child: Container(
        width: 140,
        margin: const EdgeInsets.only(right: 12),
        decoration: BoxDecoration(
          gradient: isSelected
              ? LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    sensor.color,
                    HSLColor.fromColor(sensor.color)
                        .withLightness(HSLColor.fromColor(sensor.color).lightness * 0.7)
                        .toColor()
                  ],
                )
              : null,
          color: isSelected ? null : Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: isSelected
                  ? HSLColor.fromColor(sensor.color)
                        .withLightness(HSLColor.fromColor(sensor.color).lightness * 0.3)
                        .toColor()
                  : Colors.grey.shade200,
              blurRadius: 6,
              spreadRadius: 1,
              offset: const Offset(0, 3),
            ),
          ],
        ),
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 10),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              sensor.icon,
              color: isSelected ? Colors.white : sensor.color,
              size: 24,
            ),
            const SizedBox(height: 6),
            Text(
              sensor.name,
              style: GoogleFonts.poppins(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: isSelected ? Colors.white : const Color(0xFF014331),
              ),
            ),
            const SizedBox(height: 2),
            Text(
              '${sensor.value} ${sensor.unit}',
              style: GoogleFonts.poppins(
                fontSize: 12,
                color: isSelected ? Colors.white : Colors.grey.shade700,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSensorVisualization(SensorData sensor) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.shade200,
            blurRadius: 6,
            spreadRadius: 1,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        children: [
          Padding(
            padding: const EdgeInsets.only(bottom: 8.0),
            child: Text(
              'Monitoring Data Real-time',
              style: GoogleFonts.poppins(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: Colors.grey.shade700,
              ),
            ),
          ),
          SizedBox(
            height: 250,
            child: _buildSensorChart(sensor),
          ),
        ],
      ),
    );
  }

  Widget _buildSensorChart(SensorData sensor) {
    final chartData = _generateChartData(sensor);
    if (chartData.isEmpty) {
      return const Center(child: Text('Belum ada data'));
    }
    final minY = chartData.map((spot) => spot.y).reduce(min) * 0.9;
    final maxY = chartData.map((spot) => spot.y).reduce(max) * 1.1;

    return Padding(
      padding: const EdgeInsets.only(right: 16, left: 0, top: 16, bottom: 12),
      child: LineChart(
        LineChartData(
          gridData: FlGridData(
            show: true,
            drawVerticalLine: true,
            horizontalInterval: maxY / 5,
            verticalInterval: 10,
            getDrawingHorizontalLine: (value) {
              return FlLine(
                color: Colors.grey.shade200,
                strokeWidth: 1,
              );
            },
            getDrawingVerticalLine: (value) {
              return FlLine(
                color: Colors.grey.shade200,
                strokeWidth: 1,
              );
            },
          ),
          titlesData: FlTitlesData(
            show: true,
            rightTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            topTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false),
            ),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 30,
                interval: 10,
                getTitlesWidget: (value, meta) {
                  int seconds = value.toInt();
                  if (seconds % 10 == 0 || seconds == 0 || seconds == 60) {
                    return Padding(
                      padding: const EdgeInsets.only(top: 8.0),
                      child: Text(
                        seconds == 0 ? 'now' : '$seconds s',
                        style: GoogleFonts.poppins(
                          color: Colors.grey.shade600,
                          fontSize: 10,
                        ),
                      ),
                    );
                  }
                  return const SizedBox();
                },
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                interval: (maxY - minY) / 4,
                getTitlesWidget: (value, meta) {
                  String displayValue = value.toStringAsFixed(
                    sensor.unit == '°C' || sensor.unit == '%' ? 1 : 0
                  );
                  return Text(
                    displayValue,
                    style: GoogleFonts.poppins(
                      color: Colors.grey.shade600,
                      fontSize: 10,
                    ),
                  );
                },
                reservedSize: 40,
              ),
            ),
          ),
          borderData: FlBorderData(
            show: true,
            border: Border(
              bottom: BorderSide(color: Colors.grey.shade300, width: 1),
              left: BorderSide(color: Colors.grey.shade300, width: 1),
            ),
          ),
          minX: 0,
          maxX: 60,
          minY: minY,
          maxY: maxY,
          lineBarsData: [
            LineChartBarData(
              spots: chartData,
              isCurved: true,
              color: sensor.color,
              barWidth: 3,
              isStrokeCapRound: true,
              dotData: const FlDotData(
                show: false,
              ),
              belowBarData: BarAreaData(
                show: true,
                color: HSLColor.fromColor(sensor.color)
                    .withAlpha(0.2)
                    .toColor(),
              ),
            ),
          ],
          lineTouchData: LineTouchData(
            touchTooltipData: LineTouchTooltipData(
              tooltipRoundedRadius: 8,
              getTooltipColor: (LineBarSpot touchedSpot) {
                return HSLColor.fromColor(Colors.white)
                    .withAlpha(0.8)
                    .toColor();
              },
              getTooltipItems: (List<LineBarSpot> touchedSpots) {
                return touchedSpots.map((LineBarSpot touchedSpot) {
                  int seconds = touchedSpot.x.round();
                  String timeText = seconds == 0 ? 'now' : '$seconds s ago';
                  return LineTooltipItem(
                    '${touchedSpot.y.toStringAsFixed(1)} ${sensor.unit}\n$timeText',
                    GoogleFonts.poppins(
                      color: sensor.color,
                      fontWeight: FontWeight.bold,
                    ),
                  );
                }).toList();
              },
            ),
          ),
        ),
      ),
    );
  }

  List<FlSpot> _generateChartData(SensorData sensor) {
    final history = sensor.history;
    final spots = <FlSpot>[];
    final int n = history.length;
    for (int i = 0; i < n; i++) {
      // Newest data is at x=0, next at x=5, ..., oldest at x=(n-1)*5
      double x = i * 5;
      spots.add(FlSpot(x, history[n - 1 - i]));
    }
    return spots;
  }
}