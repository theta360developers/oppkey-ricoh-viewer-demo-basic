import 'package:envied/envied.dart';

part 'env.g.dart';

@Envied(path: '.env', obfuscate: true)
final class Env {
  @EnviedField(varName: 'CLIENT_ID')
  static String clientId = _Env.clientId;
  @EnviedField(varName: 'CLIENT_SECRET')
  static String clientSecret = _Env.clientSecret;
  @EnviedField(varName: 'PRIVATE_KEY')
  static String privateKey = _Env.privateKey;
}
