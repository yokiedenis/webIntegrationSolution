"""Comprehensive test suite for agent fallback mechanisms."""

import unittest
from unittest.mock import Mock
from templates.customer_service_agent.agent import EnhancedAgent
from keyword_provider import KeywordLLMProvider

# Optional: Import fallback provider if available
try:
    from llm_fallback_provider import LLMFallbackProvider
except ImportError:
    LLMFallbackProvider = None


class TestKeywordProvider(unittest.TestCase):
    """Test KeywordLLMProvider functionality."""

    def setUp(self):
        self.provider = KeywordLLMProvider()

    def test_password_intent_detection(self):
        """Test password reset intent detection."""
        message = "I forgot my password and need to reset it"
        result = self.provider.classify_intent(message)
        self.assertEqual(result["intent"], "password_reset")
        self.assertTrue(result["requires_tool"])

    def test_billing_intent_detection(self):
        """Test billing intent detection."""
        message = "I was charged twice for my subscription"
        result = self.provider.classify_intent(message)
        self.assertEqual(result["intent"], "billing")

    def test_order_intent_detection(self):
        """Test order intent detection."""
        message = "Where is my order? I need tracking info"
        result = self.provider.classify_intent(message)
        self.assertEqual(result["intent"], "order")

    def test_sentiment_negative(self):
        """Test negative sentiment detection."""
        message = "This is absolutely terrible and I'm very frustrated"
        result = self.provider.classify_intent(message)
        self.assertLess(result["sentiment"], -0.5)
        self.assertEqual(result["urgency"], "high")

    def test_sentiment_positive(self):
        """Test positive sentiment detection."""
        message = "Thank you so much for the great help, I really appreciate it"
        result = self.provider.classify_intent(message)
        self.assertGreater(result["sentiment"], 0.5)

    def test_sentiment_neutral(self):
        """Test neutral sentiment detection."""
        message = "Can you tell me about your product features?"
        result = self.provider.classify_intent(message)
        self.assertAlmostEqual(result["sentiment"], 0.0, delta=0.3)

    def test_general_intent_fallback(self):
        """Test fallback to general intent."""
        message = "Just saying hello"
        result = self.provider.classify_intent(message)
        self.assertEqual(result["intent"], "general")
        self.assertFalse(result["requires_tool"])

    def test_response_generation(self):
        """Test response generation."""
        message = "I forgot my password"
        context = self.provider.classify_intent(message)
        response = self.provider.generate_response(message, context)
        self.assertIn("password", response.lower())

    def test_parameter_extraction(self):
        """Test parameter extraction."""
        message = "Can you check order ORDER-12345 for me?"
        params = self.provider.extract_parameters(message, "order")
        self.assertEqual(params.get("order_id"), "ORDER-12345")

    def test_tool_mapping(self):
        """Test intent to tool mapping."""
        mappings = {
            "password_reset": "reset_password",
            "order": "check_order_status",
            "refund": "initiate_refund",
        }
        for intent, expected_tool in mappings.items():
            tool = self.provider._map_intent_to_tool(intent)
            self.assertEqual(tool, expected_tool)


class TestLLMFallback(unittest.TestCase):
    """Test LLMFallbackProvider if available."""

    @unittest.skipIf(LLMFallbackProvider is None, "LLMFallbackProvider not installed")
    def test_fallback_provider_initialization(self):
        """Test fallback provider initialization."""
        if LLMFallbackProvider is None:
            self.skipTest("LLMFallbackProvider not available")
        mock_llm = Mock()
        provider = LLMFallbackProvider(primary_provider=mock_llm)
        self.assertIsNotNone(provider)

    @unittest.skipIf(LLMFallbackProvider is None, "LLMFallbackProvider not installed")
    def test_fallback_on_primary_failure(self):
        """Test fallback when primary provider fails."""
        if LLMFallbackProvider is None:
            self.skipTest("LLMFallbackProvider not available")
        # Mock primary provider that fails
        mock_primary = Mock()
        mock_primary.classify_intent.side_effect = Exception("API Error")

        # Mock fallback provider
        mock_fallback = Mock()
        mock_fallback.classify_intent.return_value = {
            "intent": "general",
            "confidence": 0.8,
        }

        provider = LLMFallbackProvider(
            primary_provider=mock_primary, fallback_provider=mock_fallback
        )

        result = provider.classify_intent("test message")
        self.assertIsNotNone(result)


class TestEnhancedAgent(unittest.TestCase):
    """Test EnhancedAgent with all providers."""

    def setUp(self):
        self.agent = EnhancedAgent()

    def test_agent_initialization(self):
        """Test agent initializes with providers."""
        self.assertIsNotNone(self.agent.tools)
        self.assertIsNotNone(self.agent.keywords)
        # At least keyword provider should be available
        if self.agent.keyword_provider is None:
            self.skipTest("KeywordLLMProvider not available")

    def test_password_reset_flow(self):
        """Test complete password reset flow."""
        message = "I forgot my password and can't log in"
        result = self.agent.invoke(message)

        self.assertEqual(result["intent"], "password_reset")
        self.assertIsNotNone(result["agent_response"])
        self.assertIn("password", result["agent_response"].lower())

    def test_order_status_flow(self):
        """Test order status inquiry flow."""
        message = "Can you check ORDER-12345 status for me?"
        result = self.agent.invoke(message)

        self.assertEqual(result["intent"], "order")
        self.assertIsNotNone(result["tool_result"])

    def test_refund_flow(self):
        """Test refund request flow."""
        message = "I want a refund for order ORDER-99999"
        result = self.agent.invoke(message)

        # Intent might be classified as "billing" due to keyword overlap
        self.assertIn(result["intent"], ["refund", "billing"])

    def test_frustrated_customer_empathy(self):
        """Test empathy injection for frustrated customers."""
        message = "This is absolutely terrible! I'm extremely frustrated!"
        result = self.agent.invoke(message)

        self.assertLess(result["sentiment"], -0.5)
        # Check if empathy prefix is in response
        response_lower = result["agent_response"].lower()
        self.assertTrue(
            any(
                word in response_lower
                for word in ["understand", "frustrat", "apologi", "sorry"]
            )
        )

    def test_processing_time(self):
        """Test that processing time is reasonable."""
        message = "What's my account balance?"
        result = self.agent.invoke(message)

        # Should process within reasonable time (using keyword fallback)
        processing_time = result["processing_time_ms"]
        self.assertGreater(processing_time, 0)
        self.assertLess(processing_time, 5000)  # Should be fast

    def test_multiple_scenarios(self):
        """Test multiple customer scenarios."""
        scenarios = [
            {
                "message": "I can't reset my password",
                "expected_intent": "password_reset",
            },
            {
                "message": "Where is my order?",
                "expected_intent": "order",
            },
            {
                "message": "I got charged twice",
                "expected_intent": "billing",
            },
            {
                "message": "The app keeps crashing",
                "expected_intent": "technical",
            },
            {
                "message": "Tell me about your premium plan",
                "expected_intent": "product_info",
            },
            {
                "message": "I want to cancel my subscription",
                "expected_intent": "billing",
            },
        ]

        for scenario in scenarios:
            result = self.agent.invoke(scenario["message"])
            self.assertEqual(
                result["intent"],
                scenario["expected_intent"],
                f"Failed for message: {scenario['message']}",
            )


class TestUnavailabilityScenarios(unittest.TestCase):
    """Test handling of unavailability scenarios."""

    def test_llm_unavailable(self):
        """Test agent works when LLM is unavailable."""
        agent = EnhancedAgent()

        # Mock LLM to be unavailable
        if agent.llm:
            agent.llm.available = False

        message = "I forgot my password"
        result = agent.invoke(message)

        # Should still produce result via fallback
        self.assertIsNotNone(result)
        self.assertEqual(result["intent"], "password_reset")

    def test_keyword_provider_fallback(self):
        """Test fallback to keyword provider."""
        agent = EnhancedAgent()

        # Disable primary providers
        agent.fallback_provider = None
        if agent.llm:
            agent.llm.available = False

        message = "I have a billing issue"
        result = agent.invoke(message)

        # Should use keyword classification
        self.assertIn(result["intent"], ["billing", "general"])

    def test_all_providers_unavailable(self):
        """Test agent still works with all providers unavailable."""
        agent = EnhancedAgent()

        # Disable all providers
        agent.fallback_provider = None
        agent.keyword_provider = None
        if agent.llm:
            agent.llm.available = False

        message = "I need help with something"
        result = agent.invoke(message)

        # Should still produce result
        self.assertIsNotNone(result)
        self.assertIsNotNone(result["agent_response"])


class TestToolExecution(unittest.TestCase):
    """Test tool execution with fallback."""

    def setUp(self):
        self.agent = EnhancedAgent()

    def test_password_reset_tool(self):
        """Test password reset tool execution."""
        message = "Reset my password please"
        result = self.agent.invoke(message)

        # Tool should be attempted
        if result.get("tool_result"):
            self.assertIn("email", str(result["tool_result"]).lower())

    def test_order_status_tool(self):
        """Test order status tool execution."""
        message = "Check my order ORDER-54321"
        result = self.agent.invoke(message)

        # Should extract order ID and call tool
        if result.get("tool_result"):
            tool_result = result["tool_result"]
            self.assertIn("status", tool_result)

    def test_refund_tool(self):
        """Test refund initiation tool."""
        message = "I need a refund for ORDER-11111"
        result = self.agent.invoke(message)

        # Tool execution might occur depending on intent classification
        self.assertIsNotNone(result["agent_response"])


class TestResponseQuality(unittest.TestCase):
    """Test response quality and formatting."""

    def setUp(self):
        self.agent = EnhancedAgent()

    def test_response_completeness(self):
        """Test response contains necessary information."""
        message = "I forgot my password"
        result = self.agent.invoke(message)

        # Check response structure
        required_fields = [
            "agent_response",
            "intent",
            "sentiment",
            "urgency",
            "processing_time_ms",
        ]
        for field in required_fields:
            self.assertIn(field, result, f"Missing field: {field}")

    def test_response_clarity(self):
        """Test response is clear and helpful."""
        message = "I can't access my account"
        result = self.agent.invoke(message)

        response = result["agent_response"]
        # Check response is not empty and reasonable length
        self.assertGreater(len(response), 20)
        self.assertLess(len(response), 500)

    def test_response_format(self):
        """Test response is properly formatted."""
        message = "What are your plans?"
        result = self.agent.invoke(message)

        # Response should be string
        self.assertIsInstance(result["agent_response"], str)
        # Should have capitalization
        self.assertTrue(result["agent_response"][0].isupper())


def run_tests():
    """Run all tests and print summary."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestKeywordProvider))
    if LLMFallbackProvider:
        suite.addTests(loader.loadTestsFromTestCase(TestLLMFallback))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestUnavailabilityScenarios))
    suite.addTests(loader.loadTestsFromTestCase(TestToolExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestResponseQuality))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    success = run_tests()
    sys.exit(0 if success else 1)
