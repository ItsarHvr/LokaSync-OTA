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
import 'package:lokasync/features/ota_update/presentation/pages/ota_update_page.dart';

void main() async {
  // Initialize the Flutter engine and binding.
  // This is necessary to ensure that the Flutter framework is properly set up.
  WidgetsFlutterBinding.ensureInitialized();
  // Initialize Firebase with options from the Firebase console.
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform
  );
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
        '/ota-update': (context) => const OTAUpdatePage(),
      },
    );
  }
}
