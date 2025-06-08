import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class OTALogEntry {
  final DateTime timestamp;
  final String nodeCodename;
  final String firmwareVersionOrigin;
  final String message;
  final Map<String, dynamic> data;
  final bool isUploaded;

  OTALogEntry({
    required this.timestamp,
    required this.nodeCodename,
    required this.firmwareVersionOrigin,
    required this.message,
    required this.data,
    this.isUploaded = false,
  });

  Map<String, dynamic> toJson() => {
    'timestamp': timestamp.toIso8601String(),
    'type': 'ap-ota-log',
    'message': message,
    'node_codename': nodeCodename,
    'firmware_version-origin': firmwareVersionOrigin,
    'data': data,
    'isUploaded': isUploaded,
  };

  static OTALogEntry fromJson(Map<String, dynamic> json) => OTALogEntry(
    timestamp: DateTime.parse(json['timestamp']),
    nodeCodename: json['node_codename'],
    firmwareVersionOrigin: json['firmware_version-origin'],
    message: json['message'],
    data: Map<String, dynamic>.from(json['data']),
    isUploaded: json['isUploaded'] ?? false,
  );
}

class OTALogStorage {
  static const _key = 'ota_log_history';

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