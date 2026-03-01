import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def setup():
    """한글 폰트 설정 (GitHub Actions + 로컬 모두 대응)"""
    candidates = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Ubuntu
        "/System/Library/Fonts/AppleGothic.ttf",             # Mac
    ]
    for path in candidates:
        try:
            fm.fontManager.addfont(path)
            plt.rcParams["font.family"] = fm.FontProperties(fname=path).get_name()
            break
        except:
            continue

    plt.rcParams["axes.unicode_minus"] = False
