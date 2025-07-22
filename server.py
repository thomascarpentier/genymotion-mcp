#!/usr/bin/env python3

import json
import os
import subprocess
from typing import Dict, List, Optional, Tuple, Any
from dotenv import load_dotenv
import time
from mcp.server.fastmcp import FastMCP


load_dotenv()



def configure_gmsaas_token(token: str):
    """Configure the gmsaas CLI with the API token."""
    if not token:
        print("Genymotion API Token not found in environment variables.")
        return
    try:
        print("Configuring gmsaas API token...")
        command = ["gmsaas", "auth", "token", token]
        subprocess.run(command, check=True, capture_output=True, text=True)
        print("gmsaas API token configured successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error configuring gmsaas API token: {e.stderr if e.stderr else e.stdout}")
        print("Please ensure the token is valid and the gmsaas command is correct.")
    except FileNotFoundError:
        print("Error: gmsaas command not found. Please ensure gmsaas is installed and in your PATH.")

# Configure the gmsaas token before initializing the server or running commands
configure_gmsaas_token(os.environ.get("GENYMOTION_API_TOKEN"))

# Initialize the MCP server
mcp = FastMCP("Genymotion SaaS MCP Server")

def run_gmsaas_command(command: List[str]) -> Dict[str, Any]:
    """Run a gmsaas command and return the results as JSON."""
    try:
        full_command = ["gmsaas", "--format", "json"] + command
        env = os.environ.copy()
        env["GMSAAS_USER_AGENT_EXTRA_DATA"] = "mcp"
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        error_message = e.stderr if e.stderr else e.stdout
        raise Exception(f"Error executing gmsaas command: {error_message}")
    except json.JSONDecodeError:
        raise Exception(f"Error parsing command output as JSON")

@mcp.tool()
def list_recipes() -> str:
    """List all available Android recipes in Genymotion SaaS."""
    try:
        result = run_gmsaas_command(["recipes", "list"])
        
        if not result:
            return "No recipes found."
        
        formatted_result = "Available recipes:\n"
        
        # Vérifier si le résultat est une liste ou une chaîne
        if isinstance(result, list):
            for recipe in result:
                formatted_result += f"- Name: {recipe.get('name', 'Unknown')}\n"
                formatted_result += f"  UUID: {recipe.get('uuid', 'Unknown')}\n"
                formatted_result += f"  OS Version: {recipe.get('os_version', 'Unknown')}\n"
                formatted_result += "\n"
        else:
            # Si c'est une chaîne, la retourner directement
            return f"Recipes information: {result}"
        
        return formatted_result
    except Exception as e:
        return f"Error listing recipes: {str(e)}"

@mcp.tool()
def get_recipe_details(recipe_uuid: str) -> str:
    """Get detailed information about a specific Android recipe."""
    try:
        result = run_gmsaas_command(["recipes", "get", recipe_uuid])
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting recipe details: {str(e)}"

@mcp.tool()
def list_running_instances() -> str:
    """List all running Android instances in Genymotion SaaS."""
    try:
        result = run_gmsaas_command(["instances", "list"])
        
        if not result:
            return "No running instances found."
        
        formatted_result = "Running instances:\n"
        
        # Vérifier si le résultat est une liste ou une chaîne
        if isinstance(result, list):
            for instance in result:
                formatted_result += f"- Name: {instance.get('name', 'Unknown')}\n"
                formatted_result += f"  UUID: {instance.get('uuid', 'Unknown')}\n"
                formatted_result += f"  State: {instance.get('state', 'Unknown')}\n"
                formatted_result += "\n"
        else:
            # Si c'est une chaîne, la retourner directement
            return f"Instances information: {result}"
        
        return formatted_result
    except Exception as e:
        return f"Error listing instances: {str(e)}"


@mcp.tool()
def start_instance(recipe_uuid: str, instance_name: str) -> str:
    """
    Start an Android instance from a recipe.
    
    Args:
        recipe_uuid: UUID of the recipe to use
        instance_name: Name to give to the new instance
    """
    try:
        command = ["instances", "start", recipe_uuid, instance_name]
        
        json_result = run_gmsaas_command(command)
        
        # Extraire les données de l'instance
        if "instance" in json_result:
            result = json_result["instance"]
        else:
            result = json_result  # Fallback au cas où la structure serait différente
        
        # Format the response
        formatted_result = f"Instance '{instance_name}' started successfully!\n"
        formatted_result += f"UUID: {result.get('uuid', 'Unknown')}\n"
        formatted_result += f"State: {result.get('state', 'Unknown')}\n"
        formatted_result += f"ADB Serial: {result.get('adb_serial', 'Unknown')}\n"
        
        # Include recipe details if available
        if "recipe" in result:
            recipe = result["recipe"]
            formatted_result += f"\nDevice Details:\n"
            formatted_result += f"- Name: {recipe.get('name', 'Unknown')}\n"
            formatted_result += f"- Android Version: {recipe.get('android_version', 'Unknown')}\n"
            formatted_result += f"- Screen: {recipe.get('screen', 'Unknown')}\n"
        
        
        return formatted_result
    except Exception as e:
        return f"Error starting instance: {str(e)}"

@mcp.tool()
def stop_instance(instance_uuid: str) -> str:
    """Stop a running Android instance."""
    try:
        run_gmsaas_command(["instances", "stop", instance_uuid])
        return f"Instance {instance_uuid} stopped successfully."
    except Exception as e:
        return f"Error stopping instance: {str(e)}"

@mcp.tool()
def connect_adb(instance_uuid: str, adb_port: Optional[int] = None) -> str:
    """
    Connect ADB to a running Android instance.
    
    Args:
        instance_uuid: UUID of the instance to connect to
        adb_port: Optional port number for ADB connection
    """
    try:
        command = ["instances", "adbconnect", instance_uuid]
        if adb_port is not None:
            command.extend(["--adb-serial-port", str(adb_port)])
            
        result = run_gmsaas_command(command)
        time.sleep(0.5)
        # Update to access the nested adb_serial
        adb_serial_value = result.get('instance', {}).get('adb_serial', 'Unknown')

        # If adb_serial is still unknown, get the instance details to get the correct value
        if adb_serial_value == 'Unknown':
            print("ADB serial unknown, getting instance details to get updated value...")
            # Use 'instances get' instead of 'instances list'
            instance_details_result = run_gmsaas_command(["instances", "get", instance_uuid])
            try:
                # The structure is different for 'get' command, the instance details are directly at the top level
                adb_serial_value = instance_details_result.get('adb_serial', 'Unknown')
                print(f"Found updated ADB serial: {adb_serial_value}")
            except Exception as e:
                print(f"Error parsing instance details result: {e}")

        return f"ADB connected to {instance_uuid}. Use ADB serial: {adb_serial_value}"
    except Exception as e:
        return f"Error connecting ADB: {str(e)}"

@mcp.tool()
def disconnect_adb(instance_uuid: str) -> str:
    """Disconnect ADB from a running Android instance."""
    try:
        run_gmsaas_command(["instances", "adbdisconnect", instance_uuid])
        return f"ADB disconnected from {instance_uuid}."
    except Exception as e:
        return f"Error disconnecting ADB: {str(e)}"


@mcp.resource("genymotion://os-versions")
def get_available_os_versions() -> str:
    """Get list of available Android OS versions."""
    try:
        result = run_gmsaas_command(["osimages", "list"])
        
        if not result:
            return "No Android OS versions found."
        
        formatted_result = "Available Android OS versions:\n"
        for image in result:
            formatted_result += f"- {image.get('os_version', 'Unknown')}\n"
        
        return formatted_result
    except Exception as e:
        return f"Error listing OS versions: {str(e)}"

@mcp.tool()
def search_recipes(recipe_name: str) -> str:
    """
    Search for recipes matching a given name and list them for selection.
    
    Args:
        recipe_name: The name or part of the name to search for
    """
    try:
        result = run_gmsaas_command(["recipes", "list"])
        
        if not result:
            return "No recipes found."
        
        # Filtrer les recipes qui correspondent au nom recherché ou à l'android_version
        matching_recipes = []
        if isinstance(result, list):
            for recipe in result:
                # Vérifie si le terme recherché est dans le nom ou dans android_version
                if (recipe_name.lower() in recipe.get('name', '').lower() or 
                    recipe_name.lower() in recipe.get('android_version', '').lower()):
                    matching_recipes.append(recipe)

        
        if not matching_recipes:
            return f"No recipes found matching '{recipe_name}'. Here are all available recipes:\n\n{list_recipes()}"
        
        formatted_result = f"Found {len(matching_recipes)} recipes matching '{recipe_name}':\n\n"
        
        for i, recipe in enumerate(matching_recipes, 1):
            formatted_result += f"{i}. Name: {recipe.get('name', 'Unknown')}\n"
            formatted_result += f"   UUID: {recipe.get('uuid', 'Unknown')}\n"
            formatted_result += f"   OS Version: {recipe.get('android_version', 'Unknown')}\n"
            formatted_result += "\n"
        
        formatted_result += "Please choose a recipe by providing its UUID for starting your instance."
        
        return formatted_result
    except Exception as e:
        return f"Error searching recipes: {str(e)}"

def main():
    mcp.run()

if __name__ == "__main__":
    # Start the MCP server when run directly
    main() 
