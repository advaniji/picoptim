<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PicOptim - JPEG Optimization Tool</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .section {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .download-btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin: 10px 0;
        }
        .download-btn:hover {
            background-color: #45a049;
        }
        .code-btn {
            background-color: #008CBA;
        }
        .instructions {
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
        }
        .warning {
            color: #dc3545;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Welcome to PicOptim</h1>
        <p>Your Easy-to-Use JPEG Optimization Tool</p>
    </div>

    <div class="section">
        <h2>Download PicOptim</h2>
        <p>Get the latest version of PicOptim here:</p>
        <a href="https://github.com/advaniji/picoptim/raw/main/picoptim.py" class="download-btn" download="picoptim.py">
            Download picoptim.py
        </a>
    </div>

    <div class="section">
        <h2>Install Dependencies</h2>
        <p>Install required Python packages using pip:</p>
        <button class="download-btn code-btn" onclick="copyToClipboard('pip install tqdm psutil argparse')">
            Copy Install Command
        </button>
        <div class="instructions">
            <ol>
                <li>Open your terminal or command prompt</li>
                <li>Paste the command: <code>pip install tqdm psutil argparse</code></li>
                <li>Press Enter to run the command</li>
            </ol>
        </div>
    </div>

    <div class="section">
        <h2>Install jpegoptim</h2>
        <p>jpegoptim is required for image optimization. Follow the instructions for your operating system:</p>
        
        <div class="instructions">
            <h3>Windows</h3>
            <ol>
                <li>Download the latest jpegoptim release from <a href="https://github.com/tjko/jpegoptim/releases" target="_blank">here</a></li>
                <li>Extract the zip file</li>
                <li>Place the jpegoptim.exe file in the same folder as your picoptim.py script</li>
            </ol>
            
            <h3>Linux</h3>
            <p>Run this command in your terminal:</p>
            <code>sudo apt-get install jpegoptim</code>

            <h3>macOS (using Homebrew)</h3>
            <p>Run this command in your terminal:</p>
            <code>brew install jpegoptim</code>
        </div>
    </div>

    <div class="section">
        <h2>Get Python</h2>
        <p>If you don't have Python installed:</p>
        <a href="https://www.python.org/downloads/" class="download-btn" target="_blank">
            Download Python
        </a>
    </div>

    <div class="section">
        <h2>Usage Instructions</h2>
        <div class="instructions">
            <h3>Basic Usage</h3>
            <p>Run the script from your terminal:</p>
            <code>python picoptim.py</code>

            <h3>Options</h3>
            <ul>
                <li><code>--lossless</code>: Lossless optimization (no quality reduction)</li>
                <li><code>--lossy</code>: Lossy optimization (reduce quality)</li>
                <li><code>--quality [1-100]</code>: Quality setting for lossy optimization</li>
                <li><code>--strip-metadata</code>: Remove image metadata</li>
                <li><code>--backup</code>: Create backup files</li>
                <li><code>--workers [number]</code>: Number of parallel workers</li>
            </ul>

            <h3>Example</h3>
            <code>python picoptim.py /path/to/images --lossy --quality 75 --strip-metadata</code>
        </div>
    </div>

    <div class="section">
        <h2>Credits</h2>
        <p>This tool uses the following excellent libraries:</p>
        <ul>
            <li><a href="https://github.com/tqdm/tqdm" target="_blank">tqdm</a> for progress bars</li>
            <li><a href="https://github.com/giampaolo/psutil" target="_blank">psutil</a> for system monitoring</li>
            <li><a href="https://github.com/tjko/jpegoptim" target="_blank">jpegoptim</a> for image optimization</li>
        </ul>
    </div>

    <script>
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(function() {
                alert('Command copied to clipboard!');
            }, function(err) {
                console.error('Failed to copy text: ', err);
            });
        }
    </script>
</body>
</html>
