import 'dart:convert';
import 'package:mqtt5_client/mqtt5_client.dart';
import 'package:mqtt5_client/mqtt5_server_client.dart';

typedef OnSensorData = void Function(Map<String, dynamic> data);

class MQTTService {
  static final MQTTService _instance = MQTTService._internal();
  factory MQTTService() => _instance;
  MQTTService._internal();

  late String server;
  late int port;
  late String topic;
  late String clientId;
  late OnSensorData onSensorData;
  String? username;
  String? password;

  late MqttServerClient client;

  void init({
    required String server,
    required int port,
    required String topic,
    required String clientId,
    required OnSensorData onSensorData,
    String? username,
    String? password,
  }) {
    this.server = server;
    this.port = port;
    this.topic = topic;
    this.clientId = clientId;
    this.onSensorData = onSensorData;
    this.username = username;
    this.password = password;
  }

  Future<void> connect() async {
    client = MqttServerClient.withPort(server, clientId, port);
    client.secure = true;
    client.logging(on: false);
    client.keepAlivePeriod = 20;
    client.onDisconnected = onDisconnected;
    client.onConnected = onConnected;
    client.onSubscribed = (subscription) => onSubscribed(subscription.topic.rawTopic ?? '');

    //final context = SecurityContext.defaultContext;
    // Load the CA certificate from assets (optional, only if needed)
    //final caBytes = await rootBundle.load('assets/ca.crt');
    //context.setTrustedCertificatesBytes(caBytes.buffer.asUint8List());
    //client.securityContext = context;
    final connMess = MqttConnectMessage()
        .authenticateAs(username ?? '', password ?? '')
        .withClientIdentifier(clientId)
        .startClean();

    client.connectionMessage = connMess;

    try {
      await client.connect();
    } catch (e) {
      client.disconnect();
      rethrow;
    }

    client.subscribe(topic, MqttQos.atLeastOnce);

    client.updates.listen((List<MqttReceivedMessage<MqttMessage>> c) {
      final recMess = c[0].payload as MqttPublishMessage;
      final pt = recMess.payload.message != null
    ? MqttPublishPayload.bytesToStringAsString(recMess.payload.message!)
    : '';

      try {
        final data = jsonDecode(pt) as Map<String, dynamic>;
        onSensorData(data);
      } catch (_) {}
    });
  }

  void disconnect() {
    client.disconnect();
  }

  void onConnected() {}
  void onDisconnected() {}
  void onSubscribed(String topic) {}
}