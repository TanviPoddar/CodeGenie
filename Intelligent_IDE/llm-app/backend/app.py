import os
import json
import subprocess
import docker
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from dotenv import load_dotenv
import tempfile
import pytest
import pylint.lint
from contextlib import redirect_stdout
import io

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

try:
    # Try the standard connection method first
    docker_client = docker.from_env()
    print("Successfully connected to Docker daemon using default connection method")
except docker.errors.DockerException as e:
    print(f"Default connection failed: {e}")
    
    # Option 2: Explicit connection to Docker socket
    try:
        docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        print("Successfully connected to Docker daemon using unix socket")
    except docker.errors.DockerException as e:
        print(f"Unix socket connection failed: {e}")
        
        # Option 3: Try with TCP connection if Docker is configured to accept TCP connections
        try:
            docker_client = docker.DockerClient(base_url='tcp://localhost:2375')
            print("Successfully connected to Docker daemon using TCP")
        except docker.errors.DockerException as e:
            print(f"TCP connection failed: {e}")
            print("Could not connect to Docker daemon. Please check Docker is running and properly configured.")

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "API is running"})

# Fix: Make sure the route is correctly defined and mapped
@app.route('/api/project-structure', methods=['GET'])
def get_project_structure():
    # Mock project structure for demonstration
    # In a real app, this would scan actual project files
    structure = [
        {"name": "src", "type": "directory"},
        {"name": "components", "type": "directory"},
        {"name": "App.js", "type": "file"},
        {"name": "index.js", "type": "file"},
        {"name": "styles.css", "type": "file"},
        {"name": "tests", "type": "directory"},
        {"name": "package.json", "type": "file"}
    ]
    return jsonify(structure)

@app.route('/api/run-code', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code')
    language = data.get('language')
    
    if not code or not language:
        return jsonify({"error": "Code and language must be provided"}), 400
    
    # Create temporary file to store code
    with tempfile.NamedTemporaryFile(delete=False, suffix=get_file_extension(language)) as temp_file:
        temp_file.write(code.encode())
        temp_file_path = temp_file.name
    
    try:
        # Execute code based on language
        output = execute_code(temp_file_path, language)
        return jsonify({"output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.route('/api/generate-tests', methods=['POST'])
def generate_tests():
    data = request.json
    code = data.get('code')
    language = data.get('language')
    
    if not code or not language:
        return jsonify({"error": "Code and language must be provided"}), 400
    
    try:
        # Generate tests using OpenAI API
        tests = generate_tests_for_code(code, language)
        
        # Run the tests and collect results
        test_results = run_tests(code, tests, language)
        return jsonify(test_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug-code', methods=['POST'])
def debug_code():
    data = request.json
    code = data.get('code')
    language = data.get('language')
    
    if not code or not language:
        return jsonify({"error": "Code and language must be provided"}), 400
    
    try:
        # Analyze code for bugs and get suggestions
        suggestions = analyze_code_for_bugs(code, language)
        return jsonify({"suggestions": suggestions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-code', methods=['POST'])
def generate_code():
    data = request.json
    prompt = data.get('prompt')
    language = data.get('language')
    
    if not prompt or not language:
        return jsonify({"error": "Prompt and language must be provided"}), 400
    
    try:
        # Generate code using OpenAI API
        generated_code = generate_code_from_prompt(prompt, language)
        return jsonify({"generatedCode": generated_code})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trigger-ci-build', methods=['POST'])
def trigger_ci_build():
    data = request.json
    code = data.get('code')
    language = data.get('language')
    
    if not code or not language:
        return jsonify({"error": "Code and language must be provided"}), 400
    
    try:
        # Trigger CI build
        build_log = run_ci_pipeline(code, language)
        return jsonify({"buildLog": build_log})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_file_extension(language):
    extensions = {
        'javascript': '.js',
        'python': '.py',
        'java': '.java',
        'csharp': '.cs',
        'cpp': '.cpp'
    }
    return extensions.get(language, '.txt')

def execute_code(file_path, language):
    execution_commands = {
        'javascript': ['node', file_path],
        'python': ['python', file_path],
        'java': ['java', file_path],
        'csharp': ['dotnet', 'run', file_path],
        # Split compile and run into separate steps for C++
        'cpp': None  # We'll handle C++ differently
    }
    
    if language == 'cpp':
        try:
            # First compile the code
            compile_result = subprocess.run(
                ['g++', file_path, '-o', 'temp_output'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if compile_result.returncode != 0:
                return f"Compilation Error: {compile_result.stderr}"
            
            # Then run the compiled program
            run_result = subprocess.run(
                ['./temp_output'], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            # Clean up compiled file
            try:
                os.remove('temp_output')
            except:
                pass
                
            if run_result.returncode != 0:
                return f"Runtime Error: {run_result.stderr}"
                
            return run_result.stdout
            
        except subprocess.TimeoutExpired:
            return "Execution timed out after 10 seconds"
        except FileNotFoundError as e:
            missing_cmd = str(e).split("'")[1]
            return f"Error: Required program '{missing_cmd}' not found. Please ensure it's installed."
        except Exception as e:
            return f"Execution error: {str(e)}"
    else:
        cmd = execution_commands.get(language)
        if not cmd:
            return f"Execution not supported for language: {language}"
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            return result.stdout
        except subprocess.TimeoutExpired:
            return "Execution timed out after 10 seconds"
        except Exception as e:
            return f"Execution error: {str(e)}"

# def execute_code(file_path, language):
#     execution_commands = {
#         'javascript': ['node', file_path],
#         'python': ['python', file_path],
#         'java': ['java', file_path],
#         'csharp': ['dotnet', 'run', file_path],
#         'cpp': ['g++', file_path, '-o', 'temp_output', '&&', './temp_output']
#     }
    
#     cmd = execution_commands.get(language)
#     if not cmd:
#         return f"Execution not supported for language: {language}"
    
#     try:
#         # Check if the command exists before executing
#         if language == 'cpp':
#             try:
#                 # Check if g++ exists
#                 subprocess.run(['which', 'g++'], check=True, capture_output=True)
#             except subprocess.CalledProcessError:
#                 return "Error: g++ compiler not found. Please install g++ to compile C++ code."
        
#         result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
#         if result.returncode != 0:
#             return f"Error: {result.stderr}"
#         return result.stdout
#     except subprocess.TimeoutExpired:
#         return "Execution timed out after 10 seconds"
#     except FileNotFoundError as e:
#         # Handle the case where the command itself is not found
#         missing_cmd = str(e).split("'")[1]
#         if missing_cmd == 'g++':
#             return f"Error: C++ compiler (g++) not found. Please install g++ to compile C++ code."
#         else:
#             return f"Error: Required program '{missing_cmd}' not found. Please ensure it's installed and in your PATH."
#     except Exception as e:
#         return f"Execution error: {str(e)}"

def generate_tests_for_code(code, language):
    # Generate tests for the provided code using OpenAI API
    prompt = f"""
    Given the following {language} code:
    
    ```{language}
    {code}
    ```
    
    Generate comprehensive test cases for this code. Include unit tests for different scenarios, edge cases, and expected behaviors. 
    Return only the test code in {language}, formatted for a common testing framework for {language}.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert software developer and tester. Generate comprehensive test cases for the provided code."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )
    
    return response.choices[0].message.content

def run_tests(code, tests, language):
    # For demonstration purposes, we'll return mock test results
    # In a real implementation, you would actually run the tests
    # and collect results
    
    # Mock test results
    mock_tests = [
        {"name": "Test basic functionality", "passed": True},
        {"name": "Test edge case: empty input", "passed": True},
        {"name": "Test edge case: large input", "passed": False, "error": "Test timed out after 5 seconds"},
        {"name": "Test error handling", "passed": True}
    ]
    
    return {
        "total": len(mock_tests),
        "passed": sum(1 for test in mock_tests if test["passed"]),
        "tests": mock_tests
    }

def analyze_code_for_bugs(code, language):
    # Use OpenAI API to analyze code for bugs
    prompt = f"""
    Analyze the following {language} code for potential bugs, inefficiencies, or best practice violations:
    
    ```{language}
    {code}
    ```
    
    For each issue, provide:
    1. The type of issue (bug, inefficiency, or style)
    2. The line number where the issue occurs
    3. A description of the issue
    4. The original problematic code snippet
    5. A suggested fix

    Return your analysis as a JSON array of objects with the following structure:
    [
      {{
        "type": "bug|inefficiency|style",
        "line": 123,
        "description": "Description of the issue",
        "originalCode": "problematic code snippet",
        "fixCode": "suggested fixed code"
      }}
    ]
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert code reviewer. Analyze the provided code for bugs and suggest fixes."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )
    
    result = response.choices[0].message.content
    
    # Extract the JSON part from the response
    try:
        # Find JSON array in the response
        start_idx = result.find('[')
        end_idx = result.rfind(']') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = result[start_idx:end_idx]
            return json.loads(json_str)
        else:
            # Parse the whole response as JSON if brackets not found
            return json.loads(result)
    except json.JSONDecodeError:
        # Return a fallback response if JSON parsing fails
        return [
            {
                "type": "style",
                "line": 1,
                "description": "Could not automatically detect specific issues. Manual code review recommended.",
                "originalCode": "",
                "fixCode": ""
            }
        ]

def generate_code_from_prompt(prompt, language):
    # Generate code based on user prompt using OpenAI API
    ai_prompt = f"""
    Write {language} code that accomplishes the following:
    
    {prompt}
    
    Return only the code, well-documented with comments explaining the approach and key parts.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"You are an expert {language} programmer. Generate clean, efficient, and well-documented code."},
            {"role": "user", "content": ai_prompt}
        ],
        max_tokens=2000
    )
    
    result = response.choices[0].message.content
    
    # Strip markdown code blocks if present
    if result.startswith("```") and result.endswith("```"):
        # Remove the first line and the last line
        lines = result.split('\n')
        if len(lines) > 2:
            result = '\n'.join(lines[1:-1])
    
    return result

def run_ci_pipeline(code, language):
    # Mock CI pipeline execution
    # In a real implementation, this would execute a series of steps:
    # 1. Run code analysis and linting
    # 2. Run tests
    # 3. Build the application
    # 4. Deploy if all checks pass
    
    log = "=== CI/CD Pipeline Started ===\n\n"
    
    # Stage 1: Code Analysis
    log += "=== Stage 1: Code Analysis ===\n"
    code_quality_issues = analyze_code_quality(code, language)
    if code_quality_issues:
        log += f"Found {len(code_quality_issues)} code quality issues:\n"
        for i, issue in enumerate(code_quality_issues, 1):
            log += f"{i}. {issue}\n"
    else:
        log += "No code quality issues found.\n"
    
    # Stage 2: Testing
    log += "\n=== Stage 2: Running Tests ===\n"
    test_results = {
        "total": 4,
        "passed": 3,
        "failed": 1
    }
    log += f"Ran {test_results['total']} tests\n"
    log += f"Passed: {test_results['passed']}\n"
    log += f"Failed: {test_results['failed']}\n"
    
    # Stage 3: Build
    log += "\n=== Stage 3: Building Application ===\n"
    log += "Building application...\n"
    log += "Build completed successfully.\n"
    
    # Stage 4: Deployment
    if test_results['failed'] == 0:
        log += "\n=== Stage 4: Deployment ===\n"
        log += "Deploying application to staging environment...\n"
        log += "Deployment successful.\n"
    else:
        log += "\n=== Stage 4: Deployment ===\n"
        log += "Deployment skipped due to test failures.\n"
    
    log += "\n=== CI/CD Pipeline Completed ===\n"
    
    return log

def analyze_code_quality(code, language):
    # Mock code quality analysis
    # In a real implementation, this would use appropriate tools for each language
    mock_issues = [
        "Line 15: Variable 'temp' is defined but never used",
        "Line 23: Consider using a more descriptive variable name than 'x'",
        "Line 42: This function is too complex (cyclomatic complexity > 10)"
    ]
    
    return mock_issues

if __name__ == '__main__':
    # Use port 3000 to match your frontend expectations
    app.run(host='0.0.0.0', port=5000, debug=True)