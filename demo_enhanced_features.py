#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JARVIS 5.0 - Enhanced Demo
Demonstrates all new integrated features

Features demonstrated:
- Wake word detection
- Google Calendar
- Weather information
- News headlines
- Wikipedia queries
- Email sending
- Jokes and entertainment
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_command_processor import EnhancedCommandProcessor
from modules.input.wake_word_detector import WakeWordDetector
from modules.input.voice_module import VoiceModule


def demo_text_mode():
    """
    Demo mode - text input instead of voice.
    Good for testing without microphone.
    """
    print("\n" + "="*70)
    print("🤖 JARVIS 5.0 - ENHANCED FEATURES DEMO (Text Mode)")
    print("="*70)
    print("\nType commands or 'sair' to exit")
    print("Type 'ajuda' to see available commands\n")
    
    # Initialize processor
    processor = EnhancedCommandProcessor()
    
    while True:
        try:
            # Get user input
            command = input("\n👤 You: ").strip()
            
            if not command:
                continue
            
            # Check for exit
            if command.lower() in ['sair', 'exit', 'quit', 'tchau']:
                print("\n🤖 JARVIS: Até logo! Até a próxima!")
                break
            
            # Process command
            result = processor.process_command(command)
            
            # Show result
            if result.get('response'):
                print(f"\n🤖 JARVIS: {result['response']}")
            
        except KeyboardInterrupt:
            print("\n\n🤖 JARVIS: Interrompido. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def demo_voice_mode():
    """
    Demo mode - voice input with wake word detection.
    Requires microphone.
    """
    print("\n" + "="*70)
    print("🤖 JARVIS 5.0 - ENHANCED FEATURES DEMO (Voice Mode)")
    print("="*70)
    
    try:
        # Initialize components
        voice = VoiceModule()
        processor = EnhancedCommandProcessor(speak_callback=voice.speak)
        detector = WakeWordDetector(
            wake_words=["jarvis", "hey jarvis", "oi jarvis"],
            timeout=30.0
        )
        
        # Check if voice is available
        if not voice.is_available():
            print("\n⚠️  Voice module not available!")
            print("Falling back to text mode...\n")
            demo_text_mode()
            return
        
        print("\n✅ Voice mode ready!")
        print("\nSay one of these wake words to activate:")
        print("  - 'Jarvis'")
        print("  - 'Hey Jarvis'")
        print("  - 'Oi Jarvis'")
        print("\nAfter activation, speak your commands.")
        print("System will auto-deactivate after 30 seconds of inactivity.")
        print("\nPress Ctrl+C to exit\n")
        
        # Command handler
        def handle_command(command: str) -> bool:
            """Process voice commands."""
            result = processor.process_command(command)
            
            # Check for exit commands
            exit_words = ['sair', 'tchau', 'bye', 'exit']
            if any(word in command.lower() for word in exit_words):
                return False
            
            return True
        
        # Start wake word detection loop
        detector.run_loop(handle_command)
        
    except KeyboardInterrupt:
        print("\n\n🤖 JARVIS: Interrompido. Até logo!")
    except Exception as e:
        print(f"\n❌ Error in voice mode: {e}")
        print("Falling back to text mode...\n")
        demo_text_mode()


def demo_quick_tests():
    """
    Quick test of all features without interaction.
    """
    print("\n" + "="*70)
    print("🧪 JARVIS 5.0 - QUICK FEATURE TESTS")
    print("="*70)
    
    processor = EnhancedCommandProcessor()
    
    test_commands = [
        ("Time Query", "que horas são"),
        ("Date Query", "que dia é hoje"),
        ("Weather", "como está o tempo em São Paulo"),
        ("News", "me conte as notícias"),
        ("Wikipedia", "quem é Albert Einstein"),
        ("Joke", "conte uma piada"),
        ("Calendar", "agenda de hoje"),
        ("Help", "ajuda"),
        ("Stats", "status")
    ]
    
    print("\n🔍 Testing all features...\n")
    
    for test_name, command in test_commands:
        print(f"\n{'='*70}")
        print(f"📝 Test: {test_name}")
        print(f"💬 Command: {command}")
        print('-'*70)
        
        try:
            result = processor.process_command(command)
            if result.get('response'):
                print(f"✅ Response: {result['response'][:200]}...")
            else:
                print("⚠️  No response")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*70)
    print("✅ Quick tests completed!")
    print("="*70)


def show_menu():
    """Show main menu."""
    print("\n" + "="*70)
    print("🤖 JARVIS 5.0 - ENHANCED FEATURES DEMO")
    print("="*70)
    print("\nSelect demo mode:")
    print("\n1. Text Mode (keyboard input - no microphone needed)")
    print("2. Voice Mode (voice input with wake word detection)")
    print("3. Quick Tests (test all features automatically)")
    print("4. Exit")
    print("\n" + "="*70)
    
    while True:
        try:
            choice = input("\nYour choice (1-4): ").strip()
            
            if choice == '1':
                demo_text_mode()
                break
            elif choice == '2':
                demo_voice_mode()
                break
            elif choice == '3':
                demo_quick_tests()
                break
            elif choice == '4':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-4.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def check_setup():
    """Check if system is properly configured."""
    print("\n🔍 Checking system configuration...\n")
    
    issues = []
    warnings = []
    
    # Check API keys
    api_keys = {
        'OPENWEATHER_API_KEY': 'Weather Service',
        'NEWS_API_KEY': 'News Service (optional, RSS fallback available)',
        'GOOGLE_CALENDAR_CREDENTIALS': 'Google Calendar',
        'EMAIL_ADDRESS': 'Email Service',
        'EMAIL_PASSWORD': 'Email Service'
    }
    
    for key, service in api_keys.items():
        if not os.getenv(key):
            if 'optional' in service.lower():
                warnings.append(f"⚠️  {key} not set - {service}")
            else:
                warnings.append(f"⚠️  {key} not set - {service} will not work")
    
    # Check imports
    try:
        import speech_recognition
        print("✅ SpeechRecognition available")
    except ImportError:
        issues.append("❌ SpeechRecognition not installed")
    
    try:
        import pyttsx3
        print("✅ pyttsx3 available")
    except ImportError:
        issues.append("❌ pyttsx3 not installed")
    
    # Show results
    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"  {issue}")
        print("\nInstall missing packages with:")
        print("  pip install -r requirements.txt")
    
    if warnings:
        print("\n💡 Optional configuration:")
        for warning in warnings:
            print(f"  {warning}")
    
    if not issues and not warnings:
        print("\n✅ All systems configured!")
    
    print("\nFor setup instructions, see: docs/ENHANCED_FEATURES.md")
    
    return len(issues) == 0


def main():
    """Main entry point."""
    print("\n" + "="*70)
    print("🤖 JARVIS 5.0 - ENHANCED FEATURES DEMO")
    print("="*70)
    print("\nCombining the best features from multiple JARVIS repositories!")
    print("\nNew Features:")
    print("  ✅ Wake word detection")
    print("  ✅ Google Calendar integration")
    print("  ✅ Weather information")
    print("  ✅ News headlines")
    print("  ✅ Wikipedia queries")
    print("  ✅ Email sending")
    print("  ✅ Jokes & entertainment")
    print("="*70)
    
    # Check setup
    if not check_setup():
        print("\n⚠️  Some features may not work due to missing configuration.")
        response = input("\nContinue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("Setup instructions: docs/ENHANCED_FEATURES.md")
            return
    
    # Show menu
    show_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
