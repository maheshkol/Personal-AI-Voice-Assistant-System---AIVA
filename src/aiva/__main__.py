import sys
sys.path.insert(0, r"E:\Personal AI Voice Assistant System - AIVA\aiva\src")

from aiva.cli.conversation_loop import ConversationLoop

if __name__ == "__main__":

    print("""
    ╔══════════════════════════════════════╗
    ║   🤖 AIVA — AI Voice Assistant       ║
    ║   By Mahesh Kolekar                  ║
    ║   University Demo Version            ║
    ╚══════════════════════════════════════╝
    """)

    print("Select mode:")
    print("  1 → Voice Mode    (full voice input/output)")
    print("  2 → Text Mode     (type input, voice output)")
    print("  3 → Hybrid Mode   (voice + text, best for demo)")

    choice = input("\nEnter choice (1/2/3): ").strip()

    # Initialize AIVA
    aiva = ConversationLoop(
        model_size="small",        # small is best for EN/HI/MR
        default_language="en",     # start in English
        use_wake_word=True
    )

    # Run selected mode
    if choice == "1":
        aiva.run_voice_mode()
    elif choice == "2":
        aiva.run_text_mode()
    elif choice == "3":
        aiva.run_hybrid_mode()
    else:
        print("Invalid choice — starting Hybrid Mode")
        aiva.run_hybrid_mode()