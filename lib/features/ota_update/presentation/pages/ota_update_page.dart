// ignore_for_file: unused_field

import 'dart:io';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'package:path/path.dart' as p;
import 'package:google_fonts/google_fonts.dart';
import 'package:lokasync/presentation/widgets/bottom_navbar.dart';


class OTAUpdatePage extends StatefulWidget {
  const OTAUpdatePage({super.key});

  @override
  State<OTAUpdatePage> createState() => _OTAUpdatePageState();
}

class _OTAUpdatePageState extends State<OTAUpdatePage> {
  File? _firmwareFile;
  String? _fileName;
  String? _ipAddress;
  String? _password;
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
      });
    }
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

final esp32TimeRegExp = RegExp(r'Download Time :\s*([\d.]+)\s*seconds', caseSensitive: false);
double? esp32Time;
final match = esp32TimeRegExp.firstMatch(response.body);
if (match != null) {
  esp32Time = double.tryParse(match.group(1)!);
}

setState(() {
  _isUploading = false;
  _uploadTime = stopwatch.elapsedMilliseconds / 1000.0;
  _uploadSpeed = total / 1024.0 / (_uploadTime ?? 1);
  double? latency;
    if (esp32Time != null && _uploadTime != null) {
      latency = _uploadTime! - esp32Time;
    }

  _log = "OTA Update Complete!\n\n"
      "Firmware Size (KBs)  : ${(_firmwareSize! / 1024).toStringAsFixed(2)} KB\n"
      "Firmware Size (Bytes): ${(_firmwareSize!).toStringAsFixed(2)} Bytes\n"
      "Upload Time (App)    : ${_uploadTime!.toStringAsFixed(2)} s\n"
      "Upload Time (ESP32)  : ${esp32Time?.toStringAsFixed(2) ?? '-'} s\n"
      "Latency              : ${latency != null ? latency.toStringAsFixed(2) : '-'} s\n\n"
      "\n\nESP32 Response:\n${response.body}";
});

    } catch (e) {
      setState(() {
        _isUploading = false;
        _log = "Error: $e";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7F9),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 16.0),
                child: Row(
                  children: [
                    InkWell(
                      onTap: () => Navigator.pushReplacementNamed(context, '/home'),
                      borderRadius: BorderRadius.circular(12),
                      child: const Icon(Icons.arrow_back, color: Color(0xFF014331), size: 24),
                    ),
                    const SizedBox(width: 32),
                    Text(
                      'Local-OTA Update',
                      style: GoogleFonts.poppins(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: const Color(0xFF014331),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              // IP Address
              TextField(
                controller: _ipController,
                decoration: InputDecoration(
                  labelText: "ESP32 AP-Mode IP Address",
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  prefixIcon: const Icon(Icons.wifi),
                ),
                keyboardType: TextInputType.numberWithOptions(decimal: true),
                enabled: !_isUploading,
              ),
              const SizedBox(height: 12),
              // Password
              TextField(
                controller: _pwController,
                decoration: InputDecoration(
                  labelText: "OTA Password",
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  prefixIcon: const Icon(Icons.lock),
                ),
                obscureText: true,
                enabled: !_isUploading,
              ),
              const SizedBox(height: 12),
              // File picker
              Row(
                children: [
                  ElevatedButton.icon(
                    onPressed: _isUploading ? null : _pickFirmware,
                    icon: const Icon(Icons.file_open),
                    label: const Text("Select .bin File"),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF014331),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      _fileName ?? "No file selected",
                      style: GoogleFonts.poppins(fontSize: 13, color: Colors.grey.shade700),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 18),
              // Upload button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _isUploading ? null : _uploadFirmware,
                  icon: const Icon(Icons.upload),
                  label: Text(_isUploading ? "Uploading..." : "Start OTA Update"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1976D2),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
              if (_isUploading)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: LinearProgressIndicator(
                    value: _progress,
                    color: const Color(0xFF1976D2),
                    backgroundColor: Colors.grey.shade300,
                  ),
                ),
              const SizedBox(height: 18),
              // Log output
              Expanded(
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.grey.shade200,
                        blurRadius: 6,
                        spreadRadius: 1,
                        offset: const Offset(0, 3),
                      ),
                    ],
                  ),
                  child: SingleChildScrollView(
                    child: Text(
                      _log,
                      style: GoogleFonts.robotoMono(fontSize: 13, color: Colors.black87),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
            ],
          ),
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