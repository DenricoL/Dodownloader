
async function download() {
    const url = document.getElementById("url").value.trim();
    const status = document.getElementById("status");

    if (!url) {
        status.textContent = "Please paste a video URL.";
        status.className = "status error";
        return;
    }

    let endpoint = "";
    let platform = "";

    if (url.includes("instagram.com")) {
        endpoint = "/download";
        platform = "Instagram";
    } else if (url.includes("tiktok.com")) {
        endpoint = "/download/tiktok";
        platform = "TikTok";
    } else {
        status.textContent = "Only Instagram and TikTok URLs are supported.";
        status.className = "status error";
        return;
    }

    status.textContent = `Downloading from ${platform}...`;
    status.className = "status loading";

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url })
        });

        if (!response.ok) {
            const error = await response.json();
            status.textContent = error.error || "Download failed.";
            status.className = "status error";
            return;
        }

        const blob = await response.blob();
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `${platform.toLowerCase()}.mp4`;
        link.click();

        status.textContent = "Download completed!";
        status.className = "status success";

    } catch (err) {
        console.error(err);
        status.textContent = "Server error. Try again later.";
        status.className = "status error";
    }
}