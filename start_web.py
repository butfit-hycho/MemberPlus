#!/usr/bin/env python3
"""
웹 UI 실행 스크립트
"""

import subprocess
import sys
import os
import webbrowser
import time
from threading import Timer

def open_browser():
    """브라우저에서 앱 열기"""
    webbrowser.open('http://localhost:8501')

def main():
    print("🌐 유효회원/휴면회원 추출 시스템 웹 UI 시작")
    print("=" * 50)
    
    # 필요한 패키지 설치 확인
    try:
        import streamlit
        print("✅ Streamlit 설치 확인")
    except ImportError:
        print("❌ Streamlit이 설치되지 않았습니다.")
        print("다음 명령어를 실행하세요: pip install -r requirements.txt")
        return
    
    # 앱 실행
    print("\n🚀 웹 서버 시작 중...")
    print("📱 브라우저에서 자동으로 열립니다.")
    print("🔗 URL: http://localhost:8501")
    print("\n⚠️  중지하려면 Ctrl+C를 누르세요.")
    print("=" * 50)
    
    # 3초 후 브라우저 열기
    Timer(3.0, open_browser).start()
    
    try:
        # Streamlit 앱 실행
        subprocess.run([
            sys.executable, 
            "-m", "streamlit", "run", 
            "app.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\n\n⏹️  서버가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        print("requirements.txt의 패키지들이 모두 설치되었는지 확인하세요.")

if __name__ == "__main__":
    main() 