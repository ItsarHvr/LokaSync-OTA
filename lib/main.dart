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
  server: "l55488bc.ala.asia-southeast1.emqxsl.com",
  port: 8883,
  topic: 'LokaSync/CloudSensor/Monitoring',
  clientId: 'mobile_${DateTime.now().millisecondsSinceEpoch % 10000}',
  username: "lokasync",
  password: "LokaSync!2345",
    onSensorData: (data) {
    
      final nodeCodename = data['node_codename'] ?? 'unknown_node';
      final nodeId = nodeCodename;
      final nodeName = nodeCodename.replaceAll('_', ' ').toUpperCase();
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

  try {
    await MQTTService().connect();
  } catch (e, st) {
    debugPrint('MQTT connection failed: $e\n$st');
    // Optionally show a dialog/snackbar later in the app
  }
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