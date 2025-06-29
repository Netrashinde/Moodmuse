import asyncio
import wave
import time
from google import genai
from google.genai import types

def generate_music(
    prompt_text="generate a happy dance song", 
    duration=10, 
    bpm=90, 
    temperature=1.0, 
    output_filename="output_music.wav"):
    
    async def main():
        client = genai.Client(api_key="AIzaSyBLFESBYhHxbQHv3fO_KATdlwWLeDnbxXc", http_options={'api_version': 'v1alpha'})

        async def receive_audio(session):
            audio_frames = []
            start_time = time.time()

            async for message in session.receive():
                if message.server_content.audio_chunks:
                    chunk = message.server_content.audio_chunks[0].data
                    audio_frames.append(chunk)
                if time.time() - start_time > duration:
                    break

            await session.stop()

            if audio_frames:
                with wave.open(output_filename, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(44100)
                    wf.writeframes(b''.join(audio_frames))
                print(f"✅ Saved audio to {output_filename}")
            else:
                print("⚠️ No audio was received.")

        async with (
            client.aio.live.music.connect(model='models/lyria-realtime-exp') as session,
            asyncio.TaskGroup() as tg,
        ):
            tg.create_task(receive_audio(session))
            await session.set_weighted_prompts([
                types.WeightedPrompt(text=prompt_text, weight=1.0)
            ])
            await session.set_music_generation_config(
                config=types.LiveMusicGenerationConfig(bpm=bpm, temperature=temperature)
            )
            print("🎵 Starting music generation...")
            await session.play()
    asyncio.run(main())



from io import BytesIO
from django.core.files.base import File

def generate_music_file(
    prompt_text="Chill",
    duration=10, 
    bpm=90, 
    temperature=1.0
):
    async def main():
        audio_stream = BytesIO()
        client = genai.Client(api_key="AIzaSyBLFESBYhHxbQHv3fO_KATdlwWLeDnbxXc", http_options={'api_version': 'v1alpha'})

        async def receive_audio(session):
            audio_frames = []
            start_time = time.time()

            async for message in session.receive():
                if message.server_content.audio_chunks:
                    chunk = message.server_content.audio_chunks[0].data
                    audio_frames.append(chunk)
                if time.time() - start_time > duration:
                    break

            await session.stop()

            if audio_frames:
                with wave.open(audio_stream, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(44100)
                    wf.writeframes(b''.join(audio_frames))
                print("✅ Audio written to BytesIO")
            else:
                print("⚠️ No audio was received.")

        async with (
            client.aio.live.music.connect(model='models/lyria-realtime-exp') as session,
            asyncio.TaskGroup() as tg,
        ):
            tg.create_task(receive_audio(session))
            await session.set_weighted_prompts([
                types.WeightedPrompt(text=prompt_text, weight=1.0)
            ])
            await session.set_music_generation_config(
                config=types.LiveMusicGenerationConfig(bpm=bpm, temperature=temperature)
            )
            print("🎵 Starting music generation...")
            await session.play()

        return audio_stream

    # Run the async code
    audio_bytes_io = asyncio.run(main())

    # Reset pointer to start for Django
    audio_bytes_io.seek(0)

    # Wrap it in a Django File object
    django_file = File(audio_bytes_io, name="generated_song.wav")

    return django_file