import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:math';
import 'package:fl_chart/fl_chart.dart';
import 'package:lokasync/presentation/widgets/bottom_navbar.dart';

// Models
class SensorData {
  final String id;
  final String name;
  final double value;
  final String unit;
  final IconData icon;
  final Color color;

  SensorData({
    required this.id,
    required this.name,
    required this.value,
    required this.unit,
    required this.icon,
    required this.color,
  });
}

class MonitoringNode {
  final String id;
  final String name;
  final List<SensorData> sensors;

  MonitoringNode({
    required this.id,
    required this.name,
    required this.sensors,
  });
}

// DataSource Interface - Untuk memudahkan implementasi API nanti
abstract class MonitoringDataSource {
  Future<List<MonitoringNode>> getNodes();
  Future<SensorData> getSensorLatestData(String nodeId, String sensorId);
}

// Mock Implementation dari DataSource untuk contoh
class MockMonitoringDataSource implements MonitoringDataSource {
  @override
  Future<List<MonitoringNode>> getNodes() async {
    // Simulasi fetch data dari API
    await Future.delayed(const Duration(milliseconds: 500));
    
    return [
      MonitoringNode(
        id: 'node1',
        name: 'Node 1',
        sensors: [
          SensorData(
            id: 'temp',
            name: 'Suhu',
            value: 28.5,
            unit: '°C',
            icon: Icons.thermostat,
            color: const Color(0xFF2E7D32),
          ),
          SensorData(
            id: 'humidity',
            name: 'Kelembaban',
            value: 75.8,
            unit: '%',
            icon: Icons.water_drop,
            color: const Color(0xFF1976D2),
          ),
        ],
      ),
      MonitoringNode(
        id: 'node2',
        name: 'Node 2',
        sensors: [
          SensorData(
            id: 'tds',
            name: 'TDS',
            value: 130.5,
            unit: 'PPM',
            icon: Icons.opacity,
            color: const Color(0xFF7B1FA2),
          ),
        ],
      ),
    ];
  }

  @override
  Future<SensorData> getSensorLatestData(String nodeId, String sensorId) async {
    // Simulasi fetch data dari API
    await Future.delayed(const Duration(milliseconds: 500));
    
    // Data dummy
    if (nodeId == 'node1' && sensorId == 'temp') {
      return SensorData(
        id: 'temp',
        name: 'Suhu',
        value: 28.5,
        unit: '°C',
        icon: Icons.thermostat,
        color: const Color(0xFF2E7D32),
      );
    } else if (nodeId == 'node1' && sensorId == 'humidity') {
      return SensorData(
        id: 'humidity',
        name: 'Kelembaban',
        value: 75.8,
        unit: '%',
        icon: Icons.water_drop,
        color: const Color(0xFF1976D2),
      );
    } else {
      return SensorData(
        id: 'tds',
        name: 'TDS',
        value: 130.5,
        unit: 'PPM',
        icon: Icons.opacity,
        color: const Color(0xFF7B1FA2),
      );
    }
  }
}

// Repository - Abstraksi untuk akses data
class MonitoringRepository {
  final MonitoringDataSource dataSource;

  MonitoringRepository({required this.dataSource});

  Future<List<MonitoringNode>> getNodes() async {
    return await dataSource.getNodes();
  }

  Future<SensorData> getSensorLatestData(String nodeId, String sensorId) async {
    return await dataSource.getSensorLatestData(nodeId, sensorId);
  }
}

// View-Model - Untuk komunikasi antara UI dan data
class MonitoringViewModel {
  final MonitoringRepository repository;
  
  MonitoringViewModel({required this.repository});
  
  Future<List<MonitoringNode>> getNodes() async {
    return await repository.getNodes();
  }
  
  Future<SensorData> getSensorLatestData(String nodeId, String sensorId) async {
    return await repository.getSensorLatestData(nodeId, sensorId);
  }
}

// Main Page
class Monitoring extends StatefulWidget {
  const Monitoring({super.key});

  @override
  State<Monitoring> createState() => _MonitoringState();
}

class _MonitoringState extends State<Monitoring> {
  // Dependency Injection
  final MonitoringViewModel _viewModel = MonitoringViewModel(
    repository: MonitoringRepository(
      dataSource: MockMonitoringDataSource(),
    ),
  );

  // Selected state
  String? _selectedNodeId;
  String? _selectedSensorId;
  
  // Data
  List<MonitoringNode> _nodes = [];
  bool _isLoading = true;
  
  // Current index untuk bottom navbar
  final int _currentIndex = 1; // 1 karena Monitoring ada di indeks 1

  @override
  void initState() {
    super.initState();
    _loadData();
  }
  
  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    
    try {
      _nodes = await _viewModel.getNodes();
      
      if (_nodes.isNotEmpty) {
        _selectedNodeId = _nodes.first.id;
        
        if (_nodes.first.sensors.isNotEmpty) {
          _selectedSensorId = _nodes.first.sensors.first.id;
        }
      }
    } catch (e) {
      // debugPrint('Error loading monitoring data: ${e.toString()}.');
      throw Exception('Error loading monitoring data: ${e.toString()}.');
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }
  
  // Mendapatkan node yang sedang dipilih
  MonitoringNode? get _selectedNode {
    if (_selectedNodeId == null) return null;
    return _nodes.firstWhere(
      (node) => node.id == _selectedNodeId,
      orElse: () => _nodes.first,
    );
  }
  
  // Mendapatkan sensor yang sedang dipilih
  SensorData? get _selectedSensor {
    final node = _selectedNode;
    if (node == null || _selectedSensorId == null) return null;
    
    try {
      return node.sensors.firstWhere(
        (sensor) => sensor.id == _selectedSensorId,
      );
    } catch (e) {
      return node.sensors.isNotEmpty ? node.sensors.first : null;
    }
  }

  // Data for charts (random data for demonstration)
  List<FlSpot> _generateChartData(SensorData sensor) {
    final random = Random();
    final spots = <FlSpot>[];
    // Generate data for the last hour (12 data points, 5 min interval)
    for (int i = 0; i < 12; i++) {
      // Base value is the current sensor value
      double baseValue = sensor.value;
      // Add some random fluctuation (±10% of the value)
      double fluctuation = (random.nextDouble() * 0.2 - 0.1) * baseValue;
      double value = (baseValue + fluctuation).clamp(0, double.infinity);
      
      // X-axis: time in minutes (60 minutes ago to now)
      double x = i * 5.0; // 5-minute intervals
      spots.add(FlSpot(x, value));
    }
    return spots;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7F9),
      body: SafeArea(
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: Color(0xFF014331)))
            : _buildContent(),
      ),
    bottomNavigationBar: BottomNavBar(
    currentIndex: _currentIndex,
    onTap: (index) {
    if (index != 3) {
      if (index == 0) {
        Navigator.pushReplacementNamed(context, '/home');
      } else if (index == 1) {
        Navigator.pushReplacementNamed(context, '/monitoring');
      } else if (index == 2) {
        Navigator.pushReplacementNamed(context, '/profile');
      }
    } else {
      Navigator.pushReplacementNamed(context, '/ota-update');
    }
  },
),
    );
  }
  
  Widget _buildContent() {
    final node = _selectedNode;
    final sensors = node?.sensors ?? [];
    
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          // Header with back button and title
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 16.0),
            child: Row(
              children: [
                InkWell(
                  onTap: () => Navigator.pushReplacementNamed(context, '/home'),
                  borderRadius: BorderRadius.circular(12),
                  child: const Icon(Icons.arrow_back, color: Color(0xFF014331), size: 24),
                ),
                const SizedBox(width: 32), // Increased from 16 to 32 for more spacing
                // Title now placed beside the back button
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
          
          // Node selector dropdown (now below title and back button)
          Padding(
            padding: const EdgeInsets.only(bottom: 16.0),
            child: _buildNodeDropdown(),
          ),
          
          // Sensor cards - scrollable horizontally
          SizedBox(
            height: 110,
            child: sensors.isEmpty
                ? const Center(
                    child: Text('Tidak ada sensor tersedia untuk node ini'),
                  )
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
          
          // Visualisasi sensor
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
    );
  }
  
  // Widget untuk dropdown pemilihan node
  Widget _buildNodeDropdown() {
    return Container(
      height: 50,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.shade200,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: _selectedNodeId,
          isExpanded: true,
          icon: const Icon(Icons.keyboard_arrow_down, color: Color(0xFF014331)),
          elevation: 0,
          style: GoogleFonts.poppins(
            color: const Color(0xFF014331),
            fontWeight: FontWeight.w500,
            fontSize: 16,
          ),
          dropdownColor: Colors.white,
          borderRadius: BorderRadius.circular(12),
          onChanged: (String? newValue) {
            if (newValue != null && newValue != _selectedNodeId) {
              setState(() {
                _selectedNodeId = newValue;
                
                // Reset selected sensor
                final sensors = _nodes
                    .firstWhere((node) => node.id == newValue)
                    .sensors;
                    
                if (sensors.isNotEmpty) {
                  _selectedSensorId = sensors.first.id;
                } else {
                  _selectedSensorId = null;
                }
              });
            }
          },
          items: _nodes.map<DropdownMenuItem<String>>((node) {
            return DropdownMenuItem<String>(
              value: node.id,
              child: Text(node.name),
            );
          }).toList(),
        ),
      ),
    );
  }
  
  // Widget untuk card sensor
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
  
  // Widget untuk visualisasi sensor
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
          // Chart title
          Padding(
            padding: const EdgeInsets.only(bottom: 8.0),
            child: Text(
              'Data dalam 1 jam terakhir',
              style: GoogleFonts.poppins(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: Colors.grey.shade700,
              ),
            ),
          ),
          
          // Chart visualization
          SizedBox(
            height: 250,
            child: _buildSensorChart(sensor),
          ),
        ],
      ),
    );
  }
  
  // New chart visualization widgets
  Widget _buildSensorChart(SensorData sensor) {
    final chartData = _generateChartData(sensor);
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
                interval: 10, // 10 minute intervals
                getTitlesWidget: (value, meta) {
                  int minutes = 60 - value.toInt();
                  if (minutes % 10 == 0 || minutes == 0 || minutes == 60) {
                    return Padding(
                      padding: const EdgeInsets.only(top: 8.0),
                      child: Text(
                        minutes == 0 ? 'now' : '$minutes min',
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
                  // Only show a reasonable number of decimal places
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
          maxX: 60, // 60 minutes
          minY: minY,
          maxY: maxY,
          lineBarsData: [
            LineChartBarData(
              spots: chartData.map((spot) => 
                FlSpot(60 - spot.x, spot.y) // Reverse x-axis (60 min ago to now)
              ).toList(),
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
                  // Calculate time (x-axis is inverted)
                  int minutesAgo = (60 - touchedSpot.x).round();
                  String timeText = minutesAgo == 0 
                      ? 'now' 
                      : '$minutesAgo min ago';
                  
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
}