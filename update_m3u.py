import re
import requests


# YAHAN APNA HOTSTAR LIVE TV API LINK DAALEIN
API_URL = "https://premiumplugx.com/htt/hot.php?playlist=1"


def make_universal():
    try:
        # API se naya token data download karna
        response = requests.get(API_URL, timeout=30)
        if response.status_code != 200:
            print("API link work nahi kar raha hai!")
            return

        lines = response.text.splitlines()
        output = ["#EXTM3U"]

        # Temp variables data hold karne ke liye
        current_inf = ""
        is_drm = False
        license_key = ""

        # Default headers jo aapki file me hain
        ua = "Hotstar;in.startv.hotstar/25.02.24.8.11169@Premium Plugx(Android/15)"
        referer = "https://hotstar.com"
        origin = "https://hotstar.com"
        cookie = ""

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#EXTM3U") or line.startswith("# JHS"):
                continue

            # 1. Info line nikalna
            if line.startswith("#EXTINF"):
                current_inf = line

            # 2. ClearKey DRM check karna
            elif "#KODIPROP:inputstream.adaptive.license_key=" in line:
                license_key = line.split(
                    "#KODIPROP:inputstream.adaptive.license_key="
                )[1].strip()
                is_drm = True

            # 3. Headers parse karna agar badalte hain
            elif "http-user-agent=" in line:
                ua = line.split("http-user-agent=")[1].strip()
            elif "http-referrer=" in line:
                referer = line.split("http-referrer=")[1].strip()
            elif "http-cookie=" in line:
                cookie = line.split("http-cookie=")[1].strip()

            # 4. Stream URL line aur processing
            elif line.startswith("http"):
                # Agar URL ke andar pehle se '|' pipe character laga ho to use saaf karna
                base_url = line.split("|")[0].strip()

                # Pipe format me headers attach karna jo sabhi players support karte hain
                universal_url = f"{base_url}|User-Agent={ua}&Referer={referer}&Origin={origin}"
                if cookie:
                    universal_url += f"&Cookie={cookie}"

                # Final structure jodna
                output.append(current_inf)

                # Agar DRM channel hai to universal DRM tags lagana (Tivimate/OTT Navigator ke liye)
                if is_drm and license_key:
                    output.append(
                        f'#KODIPROP:inputstream.adaptive.license_key="{license_key}"'
                    )
                    output.append(
                        "#KODIPROP:inputstream.adaptive.license_type=clearkey"
                    )
                    output.append("#KODIPROP:inputstream.adaptive.manifest_type=mpd")

                output.append(universal_url)

                # Variables ko agle channel ke liye reset karna
                is_drm = False

        # playlist.m3u file generate karna
        with open("playlist.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        print("M3U Playlist successfully updated!")

    except Exception as e:
        print(f"Error aaya: {e}")


if __name__ == "__main__":
    make_universal()
