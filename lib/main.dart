import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:lokasync/firebase_options.dart';
import 'package:lokasync/presentation/screens/splash_screen.dart';
import 'package:lokasync/features/auth/presentation/pages/forgotpassword_page.dart';
import 'package:lokasync/features/auth/presentation/pages/login_page.dart';
import 'package:lokasync/features/auth/presentation/pages/register_page.dart';
import 'package:lokasync/features/home/presentation/pages/home_page.dart';
import 'package:lokasync/features/monitoring/presentation/pages/monitoring_page.dart';
import 'package:lokasync/features/profile/presentation/pages/profile_page.dart';
import 'package:lokasync/features/ota_update/presentation/pages/local_update_page.dart';
import 'package:lokasync/utils/mqtt_service.dart';
import 'package:lokasync/utils/sensor_data_holder.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );

  MQTTService().init(
    server: 'i139f81d.ala.eu-central-1.emqxsl.com',
    port: 8883,
    topic: 'LokaSync/CloudSensor/Monitoring',
    clientId: 'flutter_monitoring_${DateTime.now().millisecondsSinceEpoch}',
    caCert: ''' 
-----BEGIN CERTIFICATE-----
MIIDrzCCApegAwIBAgIQCDvgVpBCRrGhdWrJWZHHSjANBgkqhkiG9w0BAQUFADBh
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBD
QTAeFw0wNjExMTAwMDAwMDBaFw0zMTExMTAwMDAwMDBaMGExCzAJBgNVBAYTAlVT
MRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5j
b20xIDAeBgNVBAMTF0RpZ2lDZXJ0IEdsb2JhbCBSb290IENBMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEA4jvhEXLeqKTTo1eqUKKPC3eQyaKl7hLOllsB
CSDMAZOnTjC3U/dDxGkAV53ijSLdhwZAAIEJzs4bg7/fzTtxRuLWZscFs3YnFo97
nh6Vfe63SKMI2tavegw5BmV/Sl0fvBf4q77uKNd0f3p4mVmFaG5cIzJLv07A6Fpt
43C/dxC//AH2hdmoRBBYMql1GNXRor5H4idq9Joz+EkIYIvUX7Q6hL+hqkpMfT7P
T19sdl6gSzeRntwi5m3OFBqOasv+zbMUZBfHWymeMr/y7vrTC0LUq7dBMtoM1O/4
gdW7jVg/tRvoSSiicNoxBN33shbyTApOB6jtSj1etX+jkMOvJwIDAQABo2MwYTAO
BgNVHQ8BAf8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUA95QNVbR
TLtm8KPiGxvDl7I90VUwHwYDVR0jBBgwFoAUA95QNVbRTLtm8KPiGxvDl7I90VUw
DQYJKoZIhvcNAQEFBQADggEBAMucN6pIExIK+t1EnE9SsPTfrgT1eXkIoyQY/Esr
hMAtudXH/vTBH1jLuG2cenTnmCmrEbXjcKChzUyImZOMkXDiqw8cvpOp/2PV5Adg
06O/nVsJ8dWO41P0jmP6P6fbtGbfYmbW0W5BjfIttep3Sp+dWOIrWcBAI+0tKIJF
PnlUkiaY4IBIqDfv8NZ5YBberOgOzW6sRBc4L0na4UU+Krk2U886UAb3LujEV0ls
YSEY1QSteDwsOoBrp+uvFRTp2InBuThs4pFsiv9kuXclVzDAGySj4dzp30d8tbQk
CAUw7C29C79Fv1C5qfPrmAESrciIxpg0X40KPMbp1ZWVbd4=
-----END CERTIFICATE----- 
''',
    username: 'lokasync',
    password: 'LokaSync!2345',
    onSensorData: (data) {
      // --- BEGIN: Store incoming data globally ---
      final nodeCodename = data['node_codename'] ?? 'unknown_node';
      final nodeId = nodeCodename;
      final nodeName = nodeCodename.replaceAll('_', ' ');
      final Map<String, SensorData> updatedSensors = {};
      data.forEach((key, value) {
        if (key == 'node_codename') return;
        final meta = sensorMeta[key] ??
            {
              'name': key,
              'unit': '',
              'icon': Icons.sensors,
              'color': Colors.grey,
            };
        final sensorId = key;
        final sensorName = meta['name'] as String;
        final sensorUnit = meta['unit'] as String;
        final sensorIcon = meta['icon'] as IconData;
        final sensorColor = meta['color'] as Color;
        final double sensorValue = (value as num).toDouble();

        final prevHistory = SensorDataHolder().nodes[nodeId]?.sensors[sensorId]?.history ?? [];
        final newHistory = List<double>.from(prevHistory)..add(sensorValue);
        if (newHistory.length > 13) newHistory.removeAt(0);

        updatedSensors[sensorId] = SensorData(
          id: sensorId,
          name: sensorName,
          value: sensorValue,
          unit: sensorUnit,
          icon: sensorIcon,
          color: sensorColor,
          history: newHistory,
        );
      });

      SensorDataHolder().updateNode(
        nodeId,
        MonitoringNode(
          id: nodeId,
          name: nodeName,
          sensors: {
            ...?SensorDataHolder().nodes[nodeId]?.sensors,
            ...updatedSensors,
          },
        ),
      );
      // --- END: Store incoming data globally ---
    },
  );
  await MQTTService().connect();

  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'LokaSync',
      theme: ThemeData(
        primarySwatch: Colors.green,
        useMaterial3: true,
      ),
      home: const SplashScreen(),
      routes: {
        '/login': (context) => const Login(),
        '/register': (context) => const Register(),
        '/forgot-password': (context) => const ForgotPassword(),
        '/home': (context) => const Home(),
        '/monitoring': (context) => const Monitoring(),
        '/profile': (context) => const Profile(),
        '/local-update': (context) => const OTAUpdatePage(),
      },
    );
  }
}