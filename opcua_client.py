import asyncio
from asyncua import Client


# ============================================================
# OPC UA CONFIGURATION
# ============================================================

OPC_UA_ENDPOINT = "opc.tcp://192.168.1.100:4840"

OPC_UA_USERNAME = ""
OPC_UA_PASSWORD = ""


# ============================================================
# TEST CONNECTION
# ============================================================

async def test_opcua_connection():

    print("")
    print("========================================")
    print("JAKCMS OPC UA CONNECTION TEST")
    print("========================================")
    print("")

    client = Client(OPC_UA_ENDPOINT)

    try:

        # ----------------------------------------------------
        # OPTIONAL USERNAME/PASSWORD
        # ----------------------------------------------------

        if OPC_UA_USERNAME and OPC_UA_PASSWORD:

            client.set_user(OPC_UA_USERNAME)
            client.set_password(OPC_UA_PASSWORD)

        # ----------------------------------------------------
        # CONNECT
        # ----------------------------------------------------

        print("Connecting to OPC UA Server...")
        print("Endpoint:", OPC_UA_ENDPOINT)

        await client.connect()

        print("")
        print("========================================")
        print("OPC UA CONNECTION SUCCESSFUL")
        print("========================================")
        print("")

        # ----------------------------------------------------
        # SERVER INFORMATION
        # ----------------------------------------------------

        server_node = client.nodes.server

        server_name = await server_node.read_browse_name()

        print("Server Name :", server_name.Name)

        # ----------------------------------------------------
        # SERVER STATUS
        # ----------------------------------------------------

        server_status = await client.nodes.server.server_status.read_value()

        print("Server State :", server_status.State)

        print("")
        print("OPC UA Server is ONLINE")

        return True

    except Exception as e:

        print("")
        print("========================================")
        print("OPC UA CONNECTION FAILED")
        print("========================================")
        print("")

        print("Error:")
        print(e)

        return False

    finally:

        try:

            await client.disconnect()

            print("")
            print("Disconnected from OPC UA Server.")

        except:

            pass


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    asyncio.run(test_opcua_connection())