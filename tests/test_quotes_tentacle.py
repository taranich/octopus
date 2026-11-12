import pytest
from tentacles.quotes_tentacle.quotes_tentacle import QuotesTentacle
from unittest.mock import MagicMock, AsyncMock
import httpx

@pytest.mark.asyncio
async def test_quotes_tentacle_run(mocker):
    mocker.patch.object(QuotesTentacle, 'load_state', return_value={})
    mocker.patch.object(QuotesTentacle, 'save_state')
    mocker.patch("asyncio.sleep", new_callable=AsyncMock) # Mock sleep

    mock_response1 = MagicMock()
    mock_response1.status_code = 200
    mock_response1.raise_for_status = MagicMock()
    mock_response1.text = "<html><body><div class='quote'><span class='text'>text</span><small class='author'>author</small></div></body></html>"

    mock_response2 = MagicMock()
    mock_response2.status_code = 200
    mock_response2.raise_for_status = MagicMock()
    mock_response2.text = "<html></html>" # Empty page

    responses = [mock_response1, mock_response2]

    async def side_effect(*args, **kwargs):
        if not responses:
            pytest.fail("httpx.AsyncClient.get called more times than expected")
        return responses.pop(0)

    tentacle = QuotesTentacle()
    mocker.patch.object(tentacle.session, "get", new_callable=AsyncMock, side_effect=side_effect)

    await tentacle.run()

    assert tentacle.session.get.call_count == 2
    tentacle.session.get.assert_any_call("http://quotes.toscrape.com/page/1/")
    tentacle.session.get.assert_any_call("http://quotes.toscrape.com/page/2/")
