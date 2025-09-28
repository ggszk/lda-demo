import requests
import json

def check_wheel_availability():
    """Python 3.13でのwheel可用性を調査"""
    
    # Python 3.13.4 (cp313) 対応状況
    packages_to_check = [
        ('pandas', '2.1.3'),
        ('pandas', '2.0.3'),
        ('pandas', '1.5.3'),
        ('numpy', '1.26.4'),
        ('scikit-learn', '1.5.1'),
        ('matplotlib', '3.9.2')
    ]
    
    print("🔍 Python 3.13 (cp313) wheel可用性調査:")
    print("=" * 60)
    
    for package, version in packages_to_check:
        url = f"https://pypi.org/pypi/{package}/{version}/json"
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            
            cp313_wheels = []
            any_wheels = []
            
            for file in data['urls']:
                if file['filename'].endswith('.whl'):
                    any_wheels.append(file['filename'])
                    if 'cp313' in file['filename'] or 'py3' in file['filename']:
                        cp313_wheels.append(file['filename'])
            
            print(f"📦 {package} {version}:")
            print(f"   総wheel数: {len(any_wheels)}")
            print(f"   Python 3.13対応: {len(cp313_wheels)}")
            
            if cp313_wheels:
                print(f"   ✅ 利用可能なwheel例: {cp313_wheels[0]}")
            else:
                print(f"   ❌ Python 3.13対応wheelなし")
                if any_wheels:
                    print(f"   📋 既存wheel例: {any_wheels[0]}")
            print()
            
        except Exception as e:
            print(f"❌ {package} {version}: エラー {e}")
            print()

if __name__ == "__main__":
    check_wheel_availability()