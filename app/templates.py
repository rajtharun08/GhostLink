GHOST_PAGE = """
<html>
    <head>
        <title>Ghosted!</title>
        <style>
            @keyframes float {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-20px); }
                100% { transform: translateY(0px); }
            }
            body { background: #121212; color: #fff; text-align: center; font-family: sans-serif; padding-top: 100px; }
            .ghost { font-size: 100px; display: inline-block; animation: float 3s ease-in-out infinite; }
            a { color: #bb86fc; text-decoration: none; border: 1px solid #bb86fc; padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="ghost">GhostLink</div>
        <h1>Link has vanished!</h1>
        <p>This URL has returned to the afterlife.</p>
        <br><br>
        <a href="/">Create New Link</a>
    </body>
</html>
"""