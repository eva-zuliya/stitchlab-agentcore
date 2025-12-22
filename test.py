from agent import StitchLabAgentApp

# Create and configure the custom app
app = StitchLabAgentApp(debug=True).configure(
    # Add your custom configuration here
    # api_key="your-key",
    # timeout=30,
).initialize()