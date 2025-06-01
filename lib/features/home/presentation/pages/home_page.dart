import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lokasync/features/auth/presentation/controllers/auth_controller.dart';
import 'package:lokasync/presentation/widgets/bottom_navbar.dart';

class Home extends StatefulWidget {
  const Home({super.key});

  @override
  State<Home> createState() => _HomeState();
}

class _HomeState extends State<Home> {
  final AuthController _authController = AuthController();
  int currentIndex = 0;
  String _filterActive = 'all';
  bool _isLoading = false;
  bool _isInitialized = false;
  String? _errorMessage;
  
  // Data statistik (nantinya akan diambil dari API)
  final Map<String, int> _statistics = {
    'total': 156,
    'success': 132,
    'failed': 24,
  };
  
  // Data aktivitas (nantinya akan diambil dari API)
  List<Map<String, dynamic>> _activities = [];
  
  @override
  void initState() {
    super.initState();
    // Use a microtask to ensure the widget is fully mounted before loading data
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeHomeData();
    });
  }
  
  // Initialize all home data with error handling
  Future<void> _initializeHomeData() async {
    try {
      if (!mounted) return;
      
      setState(() {
        _isLoading = true;
        _errorMessage = null;
      });
      
      // Check if the user is authenticated
      final user = _authController.getCurrentUser();
      if (user == null) {
        // Handle case where user is not properly authenticated
        setState(() {
          _errorMessage = "User authentication issue. Please login again.";
          _isLoading = false;
        });
        
        // Navigate back to login after a brief delay
        Future.delayed(const Duration(seconds: 2), () {
          if (mounted) {
            Navigator.of(context).pushReplacementNamed('/login');
          }
        });
        return;
      }
      
      // Load activities once we confirm user is authenticated
      await _loadActivities('all');
      
      if (mounted) {
        setState(() {
          _isInitialized = true;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = "Failed to load data: ${e.toString()}";
          _isLoading = false;
        });
      }
    }
  }
  
  // Method untuk memuat aktivitas berdasarkan filter
  Future<void> _loadActivities(String filter) async {
    try {
      if (!mounted) return;
      
      setState(() {
        _isLoading = true;
        _filterActive = filter;
      });
      
      // Simulasi loading dari API
      await Future.delayed(const Duration(seconds: 1));
      
      // Contoh data dummy (nantinya akan diganti dengan request ke API)
      List<Map<String, dynamic>> dummyData = [];
      
      if (filter == 'all' || filter == 'success') {
        dummyData.addAll([
          {
            'id': '001',
            'title': 'Monitoring Suhu',
            'timestamp': DateTime.now().subtract(const Duration(hours: 2)),
            'status': 'success',
            'value': '28°C',
          },
          {
            'id': '002',
            'title': 'Monitoring Kelembaban',
            'timestamp': DateTime.now().subtract(const Duration(hours: 4)),
            'status': 'success',
            'value': '75%',
          },
        ]);
      }
      
      if (filter == 'all' || filter == 'failed') {
        dummyData.addAll([
          {
            'id': '003',
            'title': 'Monitoring pH Tanah',
            'timestamp': DateTime.now().subtract(const Duration(hours: 6)),
            'status': 'failed',
            'errorMsg': 'Sensor tidak terhubung',
          },
        ]);
      }
      
      if (!mounted) return;
      
      setState(() {
        _activities = dummyData;
        _isLoading = false;
      });
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = "Failed to load activities: ${e.toString()}";
          _isLoading = false;
        });
      }
    }
  }
  
  // Mendapatkan nama depan pengguna
  String _getFirstName() {
    final user = _authController.getCurrentUser();
    if (user != null && user.fullName.isNotEmpty) {
      return user.fullName.split(' ')[0]; // Ambil nama depan saja
    }
    return 'User';
  }
  
void _onItemTapped(int index) {
  if (index == currentIndex) return;

  if (index == 1) {
    Navigator.pushReplacementNamed(context, '/monitoring');
  } else if (index == 2) {
    Navigator.pushReplacementNamed(context, '/profile');
  } else if (index == 3) {
    Navigator.pushReplacementNamed(context, '/ota-update');
  }
}
  
  @override
  Widget build(BuildContext context) {
    // If there's an error, show error state
    if (_errorMessage != null) {
      return Scaffold(
        backgroundColor: const Color(0xFFF5F7F9),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.error_outline,
                color: Colors.red,
                size: 60,
              ),
              const SizedBox(height: 16),
              Text(
                'Error',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 32.0),
                child: Text(
                  _errorMessage!,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 16,
                  ),
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    _errorMessage = null;
                  });
                  _initializeHomeData();
                },
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }
    
    // If still loading and not initialized, show a proper loading screen
    if (_isLoading && !_isInitialized) {
      return Scaffold(
        backgroundColor: const Color(0xFFF5F7F9),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircularProgressIndicator(
                color: Color(0xFF014331),
              ),
              const SizedBox(height: 24),
              Text(
                'Loading LokaSync data...',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey.shade700,
                ),
              ),
            ],
          ),
        ),
      );
    }
    
    // Regular home screen UI once initialized
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
                          color: Color(0xFF014331),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Selamat datang di LokaSync',
                        style: GoogleFonts.roboto(
                          fontSize: 14,
                          color: Colors.grey,
                        ),
                      ),
                    ],
                  ),
                  GestureDetector(
                    onTap: () {
                      // Navigate to profile using named route for consistency
                      Navigator.pushReplacementNamed(context, '/profile');
                    },
                    child: CircleAvatar(
                      backgroundColor: const Color(0xFF014331),
                      radius: 24,
                      child: Icon(
                        Icons.person,
                        color: Colors.white,
                        size: 28,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            
            // Statistics cards
            SizedBox(
              height: 150,
              child: ListView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 12),
                children: [
                  _buildStatCard('Total Activities', _statistics['total']!, Icons.analytics_outlined, Colors.blue),
                  _buildStatCard('Success', _statistics['success']!, Icons.check_circle_outline, Colors.green),
                  _buildStatCard('Failed', _statistics['failed']!, Icons.error_outline, Colors.red),
                ],
              ),
            ),
            
            // Filter buttons
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
              child: Row(
                children: [
                  _buildFilterButton('All Activities', 'all'),
                  const SizedBox(width: 10),
                  _buildFilterButton('Success', 'success'),
                  const SizedBox(width: 10),
                  _buildFilterButton('Failed', 'failed'),
                ],
              ),
            ),
            
            // Activities content
            Expanded(
              child: _isLoading
                  ? const Center(
                      child: CircularProgressIndicator(
                        color: Color(0xFF014331),
                      ),
                    )
                  : _activities.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.hourglass_empty,
                                size: 50,
                                color: Colors.grey.shade400,
                              ),
                              const SizedBox(height: 16),
                              Text(
                                'Tidak ada aktivitas $_filterActive',
                                style: TextStyle(
                                  fontSize: 16,
                                  color: Colors.grey.shade600,
                                ),
                              ),
                            ],
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          itemCount: _activities.length,
                          itemBuilder: (context, index) {
                            final activity = _activities[index];
                            return _buildActivityCard(activity);
                          },
                        ),
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
  
  // Card untuk statistik dengan gradient warna
  Widget _buildStatCard(String title, int value, IconData icon, Color color) {
    // Tentukan gradient warna berdasarkan jenis kartu
    Gradient gradient;
    Color shadowColor;
    
    if (title.contains('Total')) {
      // Gradient biru untuk total activities
      gradient = const LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [Color(0xFF2196F3), Color(0xFF4FC3F7)],
      );
      shadowColor = const Color.fromRGBO(33, 150, 243, 0.3); // Warna biru dengan opacity 0.3
    } else if (title.contains('Success')) {
      // Gradient hijau untuk success
      gradient = const LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [Color(0xFF2E7D32), Color(0xFF66BB6A)],
      );
      shadowColor = const Color.fromRGBO(46, 125, 50, 0.3); // Warna hijau dengan opacity 0.3
    } else {
      // Gradient merah untuk failed
      gradient = const LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [Color(0xFFB71C1C), Color(0xFFE57373)],
      );
      shadowColor = const Color.fromRGBO(183, 28, 28, 0.3); // Warna merah dengan opacity 0.3
    }
    
    return Container(
      width: 150,
      margin: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        gradient: gradient,
        boxShadow: [
          BoxShadow(
            // Menggunakan warna shadow yang sudah ditentukan
            color: shadowColor,
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
              size: 32,
            ),
            const SizedBox(height: 12),
            Text(
              value.toString(),
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: const TextStyle(
                fontSize: 12,
                color: Colors.white,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  // Button untuk filter aktivitas - lebih kecil dan lebih rounded
  Widget _buildFilterButton(String title, String filterValue) {
    final isActive = _filterActive == filterValue;
    return Expanded(
      child: ElevatedButton(
        onPressed: () {
          if (!isActive) {
            _loadActivities(filterValue);
          }
        },
        style: ElevatedButton.styleFrom(
          backgroundColor: isActive ? const Color(0xFF014331) : Colors.white,
          foregroundColor: isActive ? Colors.white : Colors.grey,
          elevation: isActive ? 2 : 0,
          padding: const EdgeInsets.symmetric(vertical: 8), // Lebih kecil vertically
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20), // Lebih rounded (oval)
            side: BorderSide(
              color: isActive ? Colors.transparent : Colors.grey.shade300,
            ),
          ),
          textStyle: const TextStyle(
            fontSize: 11, // Font size lebih kecil
            fontWeight: FontWeight.w600,
          ),
        ),
        child: Text(title),
      ),
    );
  }
  
  // Card untuk aktivitas dengan latar belakang putih polos
  Widget _buildActivityCard(Map<String, dynamic> activity) {
    final bool isSuccess = activity['status'] == 'success';
    final Color statusColor = isSuccess ? Colors.green : Colors.red;
    final IconData statusIcon = isSuccess ? Icons.check_circle : Icons.error;
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white, // Background putih polos
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            // Mengganti withOpacity dengan warna yang memiliki alpha
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
                // Ganti withOpacity dengan Color yang memiliki alpha yang tepat
                color: isSuccess
                    ? Color.fromRGBO(0, 128, 0, 0.1) // Green dengan alpha 0.1
                    : Color.fromRGBO(255, 0, 0, 0.1), // Red dengan alpha 0.1
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
                    activity['title'],
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF014331),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    isSuccess
                        ? 'Value: ${activity['value']}'
                        : 'Error: ${activity['errorMsg']}',
                    style: TextStyle(
                      fontSize: 14,
                      color: isSuccess ? Colors.black54 : statusColor,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _formatDateTime(activity['timestamp']),
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade500,
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
  
  // Helper untuk format tanggal
  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }
}