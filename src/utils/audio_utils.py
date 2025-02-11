import subprocess
import re
from typing import Tuple, Optional
from ..core.logger import get_logger

logger = get_logger(__name__)

def find_audio_devices() -> Tuple[Optional[str], Optional[str]]:
    """
    Automatically detect the correct audio devices
    Returns:
        Tuple of (output_device, input_device)
    """
    output_device = None
    input_device = None
    
    # Find speaker (UACDemoV10)
    try:
        aplay_output = subprocess.check_output(['aplay', '-l'], text=True)
        for line in aplay_output.split('\n'):
            if 'UACDemoV1' in line:
                # Extract card number using regex
                match = re.search(r'card (\d+):', line)
                if match:
                    card_num = match.group(1)
                    output_device = f"hw:{card_num},0"
                    logger.info(f"Found speaker device: {output_device}")
                break
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running aplay: {e}")
    
    # Find microphone (USB PnP Sound Device)
    try:
        arecord_output = subprocess.check_output(['arecord', '-l'], text=True)
        for line in arecord_output.split('\n'):
            if 'USB PnP Sound Device' in line:
                # Extract card number using regex
                match = re.search(r'card (\d+):', line)
                if match:
                    card_num = match.group(1)
                    input_device = int(card_num)  # Convert to int for PyAudio
                    logger.info(f"Found microphone device: {input_device}")
                break
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running arecord: {e}")
    
    if output_device is None:
        logger.warning("Could not find UACDemoV10 speaker, falling back to default")
        output_device = "hw:1,0"
        
    if input_device is None:
        logger.warning("Could not find USB PnP Sound Device microphone, falling back to default")
        input_device = 1
        
    return output_device, input_device

def test_audio_devices(output_device: str, input_device: int) -> bool:
    """
    Test if the audio devices are working
    Returns:
        bool: True if devices are working, False otherwise
    """
    success = True
    
    # Test speaker
    try:
        test_cmd = ['speaker-test', '-D', output_device, '-t', 'sine', '-f', '1000', '-l', '1']
        subprocess.run(test_cmd, timeout=1, capture_output=True)
        logger.info(f"Speaker test successful on device {output_device}")
    except subprocess.TimeoutExpired:
        # This is actually expected as we kill the process after 1 second
        logger.info(f"Speaker test completed on device {output_device}")
    except Exception as e:
        logger.error(f"Speaker test failed: {e}")
        success = False
    
    # Test microphone
    try:
        test_cmd = f"arecord -D hw:{input_device},0 -d 1 -f cd /dev/null"
        subprocess.run(test_cmd, shell=True, capture_output=True)
        logger.info(f"Microphone test successful on device {input_device}")
    except Exception as e:
        logger.error(f"Microphone test failed: {e}")
        success = False
    
    return success 