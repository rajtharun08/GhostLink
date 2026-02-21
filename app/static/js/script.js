async function shorten() {
    const btn = document.getElementById('gen-btn');
    const resultSection = document.getElementById('result-section');
    const output = document.getElementById('short-url-output');
    
    
    const payload = {
        long_url: document.getElementById('longUrl').value,
        max_clicks: parseInt(document.getElementById('maxClicks').value),
        ttl_hours: parseInt(document.getElementById('ttlHours').value),
        custom_code: document.getElementById('customCode').value || null
    };

    
    btn.innerText = "GHOSTING...";
    btn.disabled = true;

    try {
        const response = await fetch('/shorten', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            output.innerHTML = `<a href="${data.short_url}" target="_blank" style="color: inherit; text-decoration: none;">${data.short_url}</a>`;
            resultSection.style.display = 'flex';
        } else {
            
            let msg = data.detail;
            if (typeof msg === 'object') msg = msg[0].msg;
            alert("Error: " + msg);
        }
    } catch (e) {
        alert("Server error. Please check your connection.");
    } finally {
        btn.innerText = "GENERATE GHOST LINK";
        btn.disabled = false;
    }
}

function copyLink() {
    const linkText = document.getElementById('short-url-output').innerText;
    const copyBtn = document.getElementById('copyBtn');
    

    navigator.clipboard.writeText(linkText).then(() => {
        copyBtn.innerText = "COPIED!";
        setTimeout(() => { copyBtn.innerText = "COPY"; }, 2000);
    });
}
