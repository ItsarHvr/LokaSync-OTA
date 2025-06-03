import 'package:flutter/material.dart';
// Make sure to import your MonitoringNode and SensorData classes if they are in another file
import 'package:lokasync/features/monitoring/presentation/pages/monitoring_page.dart';

class SensorDataHolder extends ChangeNotifier {
  static final SensorDataHolder _instance = SensorDataHolder._internal();
  factory SensorDataHolder() => _instance;
  SensorDataHolder._internal();

  // Holds all nodes and their sensors
  final Map<String, MonitoringNode> nodes = {};

  // Update or add a node and notify listeners
  void updateNode(String nodeId, MonitoringNode node) {
    nodes[nodeId] = node;
    notifyListeners();
  }

  // Optionally: update a single sensor in a node
  void updateSensor(String nodeId, String sensorId, SensorData sensor) {
    final node = nodes[nodeId];
    if (node != null) {
      final updatedSensors = Map<String, SensorData>.from(node.sensors);
      updatedSensors[sensorId] = sensor;
      nodes[nodeId] = node.copyWith(sensors: updatedSensors);
      notifyListeners();
    }
  }

  // Optionally: clear all data
  void clear() {
    nodes.clear();
    notifyListeners();
  }
}