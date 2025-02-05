import os
import pvporcupine  

def test_porcupine():
    access_key = os.getenv('PORCUPINE_ACCESS_KEY')
    if not access_key:
        print("Access key not found in environment variables.")
        return
    try:
        porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=["Cesso"],
            keyword_paths=["./Cesso_it_raspberry-pi_v3_0_0.ppn"]
        )
        print("Porcupine initialized successfully.")
        porcupine.delete()
    except Exception as e:
        print(f"Porcupine initialization failed: {e}")

if __name__ == "__main__":
    test_porcupine()
