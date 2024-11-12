import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_inappwebview/flutter_inappwebview.dart';
import 'env.dart';
import 'package:dart_jsonwebtoken/dart_jsonwebtoken.dart';

WebViewEnvironment? webViewEnvironment;

Future main() async {
  WidgetsFlutterBinding.ensureInitialized();

  if (!kIsWeb && defaultTargetPlatform == TargetPlatform.windows) {
    final availableVersion = await WebViewEnvironment.getAvailableVersion();
    assert(availableVersion != null,
        'Failed to find an installed WebView2 Runtime or non-stable Microsoft Edge installation.');

    webViewEnvironment = await WebViewEnvironment.create(
        settings:
            WebViewEnvironmentSettings(userDataFolder: 'YOUR_CUSTOM_PATH'));
  }

  if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
    await InAppWebViewController.setWebContentsDebuggingEnabled(kDebugMode);
  }

  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  InAppWebViewSettings settings = InAppWebViewSettings(
      isInspectable: kDebugMode,
      mediaPlaybackRequiresUserGesture: false,
      allowsInlineMediaPlayback: true,
      iframeAllow: "camera; microphone",
      iframeAllowFullscreen: true);
  String viewerToken =
      'please generate viewer token  with your private key first';

  @override
  Widget build(BuildContext context) {
    debugPrint('client ID: ${Env.clientId}');
    debugPrint('private key: ${Env.privateKey}');
    debugPrint('client secret: ${Env.clientSecret}');
// Generate a JSON Web Token
// You can provide the payload as a key-value map or a string
    final jwt = JWT(
      // Payload
      {
        'client_id': Env.clientId,
      },
    );

// Sign it (default with HS256 algorithm)
    final token = jwt.sign(SecretKey(Env.privateKey));

    print('Signed token: $token\n');
    return MaterialApp(
      home: Scaffold(
          appBar: AppBar(title: const Text("JavaScript Handlers")),
          body: SafeArea(
              child: Column(children: <Widget>[
            Expanded(
              flex: 1,
              child: Row(
                children: [
                  ElevatedButton(
                    onPressed: () {
                      setState(() {
                        viewerToken = token;
                      });
                    },
                    child: const Text('token'),
                  ),
                ],
              ),
            ),
            Expanded(
              flex: 1,
              child: SingleChildScrollView(
                  child: Padding(
                padding: const EdgeInsets.all(8.0),
                child: Text(viewerToken),
              )),
            ),
            Expanded(
              flex: 6,
              child: InAppWebView(
                webViewEnvironment: webViewEnvironment,
                initialData: InAppWebViewInitialData(data: """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
       <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/pannellum@2.5.6/build/pannellum.css"/>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/pannellum@2.5.6/build/pannellum.js"></script>
    <style>
    #panorama {
        width: 600px;
        height: 400px;
    }
    </style>
    </head>
    <body>
        <h1>JavaScript Handlers</h1>
        <script>
            window.addEventListener("flutterInAppWebViewPlatformReady", function(event) {
                window.flutter_inappwebview.callHandler('handlerUrl')
                  .then(function(result) {
                    // print to the console the data coming
                    // from the Flutter side.
                    console.log('console log from JavaScript webview: ', JSON.stringify(result));

                    window.flutter_inappwebview
                      .callHandler('handlerFooWithArgs', 1, true, ['bar', 5], {foo: 'baz'}, result);
                });
            });
        </script>

        <div id="panorama"></div>
<script>
pannellum.viewer('panorama', {
    "type": "equirectangular",
    "panorama": "https://pannellum.org/images/alma.jpg"
});
</script>
    </body>
</html>
                      """),
                initialSettings: settings,
                onWebViewCreated: (controller) {
                  controller.addJavaScriptHandler(
                      handlerName: 'handlerUrl',
                      callback: (JavaScriptHandlerFunctionData data) {
                        // return data to the JavaScript side!
                        return {
                          'token': 'long token goes here',
                          'contentId': 'contentId goes here'
                        };
                      });

                  controller.addJavaScriptHandler(
                      handlerName: 'handlerFooWithArgs',
                      callback: (JavaScriptHandlerFunctionData data) {
                        print(data);
                        // it will print:
                        // JavaScriptHandlerFunctionData{args: [1, true, [bar, 5], {foo: baz}, {bar: bar_value, baz: baz_value}], isMainFrame: true, origin: , requestUrl: about:blank}
                      });
                },
                onConsoleMessage: (controller, consoleMessage) {
                  print(consoleMessage);
                  // it will print: {message: {"bar":"bar_value","baz":"baz_value"}, messageLevel: 1}
                },
              ),
            ),
          ]))),
    );
  }
}
