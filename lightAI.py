import os
from brain import generate_response, parse_tool_call
from network_tools import (
    check_wifi_status,
    check_ethernet_status,
    connect_to_wifi,
    disconnect_wifi,
    enable_adapter,
    disable_adapter,
    list_adapters,
    check_internet,
)


def main():
    """Main conversation loop for LightAI."""
    print("\n" + "=" * 60)
    print("Welcome! I'm LightAI, your intelligent network assistant.")
    print("I'm running completely locally - no internet required!")
    print("Type 'quit' or 'exit' to leave.")
    print("=" * 60 + "\n")

    conversation_history = []
    system_prompt = """You are LightAI, an intelligent AI assistant specialized in network tasks on Windows.
You can help users with:
- Checking WIFI and Ethernet status
- Connecting/disconnecting from WIFI networks
- Enabling/disabling network adapters
- Listing available adapters
- Checking internet connectivity

Be conversational, helpful, and professional. When a user asks for a network action, offer to perform it.
If you're going to perform an action, state clearly what you're about to do."""

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nLightAI: Thank you for using LightAI. Goodbye!")
                break

            conversation_history.append(user_input)
            history_context = "\n".join(conversation_history[-6:])

            prompt = f"""[INST] System: {system_prompt}

Recent conversation:
{history_context}

User: {user_input}

LightAI: [/INST]"""

            print("\nLightAI: ", end="", flush=True)
            response = generate_response(prompt, max_length=400)
            print(response)

            tool_call = parse_tool_call(response)
            if tool_call:
                tool_name, tool_args = tool_call
                result = ""
                if tool_name == "check_wifi_status":
                    result = check_wifi_status()
                elif tool_name == "check_ethernet_status":
                    result = check_ethernet_status()
                elif tool_name == "connect_to_wifi":
                    ssid = tool_args.get("ssid", "")
                    if ssid:
                        print(f"\n[Connecting to {ssid}...]")
                        result = connect_to_wifi(ssid)
                    else:
                        result = "No network name provided."
                elif tool_name == "disconnect_wifi":
                    print("\n[Disconnecting from WIFI...]")
                    result = disconnect_wifi()
                elif tool_name == "enable_adapter":
                    name = tool_args.get("name", "")
                    if name:
                        print(f"\n[Enabling {name}...]")
                        result = enable_adapter(name)
                    else:
                        result = "No adapter name provided."
                elif tool_name == "disable_adapter":
                    name = tool_args.get("name", "")
                    if name:
                        print(f"\n[Disabling {name}...]")
                        result = disable_adapter(name)
                    else:
                        result = "No adapter name provided."
                elif tool_name == "list_adapters":
                    print("\n[Listing adapters...]")
                    result = list_adapters()
                elif tool_name == "check_internet":
                    print("\n[Checking internet...]")
                    result = check_internet()

                if result:
                    followup_prompt = f"""[INST] Based on this result from the network tool:\n\n{result}\n\nBriefly summarize the result for the user in one or two sentences. [/INST]"""
                    print("\nLightAI: ", end="", flush=True)
                    followup = generate_response(followup_prompt, max_length=150)
                    print(followup)
                    conversation_history.append(f"LightAI executed action with result: {result}")

            conversation_history.append(f"LightAI: {response}")

        except KeyboardInterrupt:
            print("\n\nLightAI: Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nLightAI: I encountered an error: {str(e)}")
            print("Please try again or ask for help.")


if __name__ == "__main__":
    main()
