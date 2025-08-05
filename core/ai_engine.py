import os
import google.generativeai as genai
from google.generativeai.types import generation_types

class GeminiClient:
    """ 
    A client class to interact with the Google API for content
    and image generation.
    """
    def __init__(self):
        """
        Initializes the Gemini client.
        It requires the GEMINI_API_KEY to be set as an environment variable.
        """
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        
        genai.configure(api_key=self.api_key)
        
        # Initialize the model for text generation
        self.text_model = genai.GenerativeModel('gemini-2.5-pro')
        
        # TODO: Initialize the model for image generation when available/chosen
        # self.image_model = genai.GenerativeModel('gemini-pro-vision') # Or the specific image model
        
    def generate_text(self, prompt: str) -> str:
        """
        Generates text content based on a given prompt.

        Args:
            prompt: The detailed prompt for the AI.

        Returns:
            The generated text as a string.
        
        Raises:
            Exception: If the API call fails for any reason.
        """
        
        try:
            response = self.text_model.generate_content(prompt)
            return response.text
        
        except generation_types.StopCandidateException as e:
            # This can happen if the model's response is blocked for safety reason.
            print(f"Error: Generation stopped due to safety settings. {e}")
            raise Exception("The generated content was blocked for safety reasons. Please try rephrasing your request.")
        except Exception as e:
            # Handle other potential API errors (invalid API key, network issues)
            print(f"An unexpected error occurred with the Gemini API: {e}")
            raise Exception("An error occurred while communicating with the AI. Please try again later. If you repeatedly see this error, please contact support@aygentx.aydie.in")
        
        
    def generate_image(self, prompt: str) -> str:
        """ 
        Generates an image based on a given prompt.

        NOTE: This is a placeholder. The actual implementation will depend on the
        specific Gemini model and library used for image generation.

        Args:
            prompt: The prompt describing the image to be generated.

        Returns:
            A URL to the generated image.        
        """
        print(f"--- SIMULATING REAL AI IMAGE GENERATION WITH PROMPT ---\n")
        # TODO: Replace this with a real call to the Gemini image generation API.
        # This might involve different library calls or endpoints.
        try: 
            # Example of what a real call might look like
            # response = self.image_model.generate_content(prompt)
            # image_url = response.image_url
            # return image_url
            
            # For now, we return a placeholder.
            return "https://placehold.co/1024x1024/4f46e5/ffffff?text=Real+AI+Image"
        except Exception as e:
            print(f"An unexpected error occured during image generation: {e}")
            raise Exception("An error occured while generating the image.")
        
# We can create a single instance to be imported across the app
# to avoid re-initializing the client repeatedly.
gemini_client = GeminiClient()