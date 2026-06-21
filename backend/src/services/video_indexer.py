import os
import logging
import yt_dlp
import cv2
import pytesseract
from faster_whisper import WhisperModel

logger = logging.getLogger("video-processor")


class VideoIndexerService:
    """
    Local video processing service.
    Replaces Azure Video Indexer with:
      - faster-whisper  → audio transcription (runs on CPU, no API key)
      - pytesseract     → on-screen text OCR  (runs on CPU, no API key)
      - opencv          → frame extraction
    """

    def __init__(self):
        # tiny  → fastest, ~40MB RAM, good for demos
        # base  → better accuracy, ~75MB RAM  ← default
        # small → best quality, ~240MB RAM
        model_size = os.getenv("WHISPER_MODEL", "base")
        logger.info(f"Loading Whisper '{model_size}' model (CPU, int8 quantized)...")
        self.whisper_model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8"   # quantized = 4x less RAM, still accurate
        )
        logger.info("Whisper model ready.")

    def download_youtube_video(self, url: str, output_path: str = "temp_audit_video.mp4") -> str:
        """Downloads a YouTube video to a local MP4 file using yt-dlp."""
        logger.info(f"Downloading YouTube video: {url}")
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            logger.info("Download complete.")
            return output_path
        except Exception as e:
            raise Exception(f"YouTube Download Failed: {str(e)}")

    def transcribe_audio(self, video_path: str) -> str:
        """
        Transcribes audio from the video using faster-whisper.
        Runs entirely locally — no API calls, no cost.
        """
        logger.info("Transcribing audio with Whisper...")
        segments, info = self.whisper_model.transcribe(
            video_path,
            beam_size=5,
            language="en"   # force English for speed; remove for multilingual
        )
        transcript = " ".join(seg.text.strip() for seg in segments)
        logger.info(f"Transcription done. Language: {info.language}, chars: {len(transcript)}")
        return transcript

    def extract_ocr_text(self, video_path: str, sample_frames: int = 8) -> list:
        """
        Samples frames evenly across the video and extracts on-screen text
        using pytesseract. Returns a deduplicated list of text strings.
        """
        logger.info(f"Running OCR on {sample_frames} sampled frames...")
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            logger.warning("Could not open video for OCR extraction.")
            return []

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        ocr_results = set()

        # Sample frames evenly across the video duration
        frame_indices = [
            int(total_frames * i / sample_frames)
            for i in range(sample_frames)
        ]

        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue
            # Grayscale improves OCR accuracy on most ad/UI text
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray, config='--psm 11').strip()
            if len(text) > 3:  # filter out single-char noise
                ocr_results.add(text)

        cap.release()
        logger.info(f"OCR complete. Found text in {len(ocr_results)} unique frames.")
        return list(ocr_results)

    def get_duration(self, video_path: str) -> float:
        """Returns video duration in seconds."""
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return round(frames / fps, 2) if fps > 0 else 0.0

    def extract_data(self, processed: dict) -> dict:
        """Pass-through: local processing already returns the correct state format."""
        return processed