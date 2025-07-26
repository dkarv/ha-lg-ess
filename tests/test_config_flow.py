"""Test the LG ESS config flow."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from ipaddress import IPv4Address, IPv6Address

from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigFlowResult

from custom_components.lg_ess.config_flow import EssConfigFlow


@pytest.fixture
def mock_hass():
    """Create a mock HomeAssistant instance."""
    hass = Mock(spec=HomeAssistant)
    hass.config_entries = Mock()
    return hass


@pytest.fixture
def config_flow(mock_hass):
    """Create a config flow instance."""
    flow = EssConfigFlow()
    flow.hass = mock_hass
    return flow


@pytest.mark.asyncio
async def test_zeroconf_ipv6_only_aborts(config_flow):
    """Test that zeroconf discovery with only IPv6 addresses aborts properly."""
    # Create discovery info with only IPv6 addresses (the problematic case)
    discovery_info = ZeroconfServiceInfo(
        ip_address=IPv6Address("2001:db8::1"),
        ip_addresses=[IPv6Address("2001:db8::1")],
        port=443,
        hostname="test-device.local.",
        type="_lg-ess._tcp.local.",
        name="test-device._lg-ess._tcp.local.",
        properties={}
    )
    
    # Call the actual async_step_zeroconf method
    result = await config_flow.async_step_zeroconf(discovery_info)
    
    # Should abort with the correct reason
    assert result["type"] == "abort"
    assert result["reason"] == "no_ipv4_address"


@pytest.mark.asyncio
async def test_zeroconf_mixed_addresses_proceeds(config_flow):
    """Test that zeroconf discovery with both IPv4 and IPv6 addresses proceeds normally."""
    # Create discovery info with both IPv4 and IPv6 addresses
    discovery_info = ZeroconfServiceInfo(
        ip_address=IPv4Address("192.168.1.100"),  # The first non-link-local address
        ip_addresses=[IPv6Address("2001:db8::1"), IPv4Address("192.168.1.100")],
        port=443,
        hostname="test-device.local.",
        type="_lg-ess._tcp.local.",
        name="test-device._lg-ess._tcp.local.",
        properties={}
    )
    
    # Mock the unique ID methods to prevent actual configuration
    with patch.object(config_flow, 'async_set_unique_id') as mock_set_uid, \
         patch.object(config_flow, '_abort_if_unique_id_configured') as mock_abort_uid, \
         patch.object(config_flow, '_async_abort_entries_match') as mock_abort_entries, \
         patch.object(config_flow, 'async_step_user') as mock_step_user:
        
        mock_step_user.return_value = {"type": "form"}
        
        # Call the actual async_step_zeroconf method
        result = await config_flow.async_step_zeroconf(discovery_info)
        
        # Should proceed to user step (form)
        assert result["type"] == "form"
        
        # Verify the expected calls were made
        mock_set_uid.assert_called_once_with("test-device")
        mock_abort_uid.assert_called_once()
        mock_abort_entries.assert_called_once_with({"host": "192.168.1.100"})
        mock_step_user.assert_called_once()


@pytest.mark.asyncio
async def test_zeroconf_ipv4_only_proceeds(config_flow):
    """Test that zeroconf discovery with only IPv4 addresses proceeds normally."""
    # Create discovery info with only IPv4 addresses
    discovery_info = ZeroconfServiceInfo(
        ip_address=IPv4Address("192.168.1.100"),
        ip_addresses=[IPv4Address("192.168.1.100")],
        port=443,
        hostname="test-device.local.",
        type="_lg-ess._tcp.local.",
        name="test-device._lg-ess._tcp.local.",
        properties={}
    )
    
    # Mock the unique ID methods to prevent actual configuration
    with patch.object(config_flow, 'async_set_unique_id') as mock_set_uid, \
         patch.object(config_flow, '_abort_if_unique_id_configured') as mock_abort_uid, \
         patch.object(config_flow, '_async_abort_entries_match') as mock_abort_entries, \
         patch.object(config_flow, 'async_step_user') as mock_step_user:
        
        mock_step_user.return_value = {"type": "form"}
        
        # Call the actual async_step_zeroconf method  
        result = await config_flow.async_step_zeroconf(discovery_info)
        
        # Should proceed to user step (form)
        assert result["type"] == "form"
        
        # Verify the expected calls were made
        mock_set_uid.assert_called_once_with("test-device")
        mock_abort_uid.assert_called_once()
        mock_abort_entries.assert_called_once_with({"host": "192.168.1.100"})
        mock_step_user.assert_called_once()


@pytest.mark.asyncio
async def test_zeroconf_no_attribute_error_with_fix():
    """Test that the fix prevents AttributeError when only IPv6 addresses are present."""
    # This test verifies that the specific bug (AttributeError accessing .version on None) 
    # does not occur with the fix in place. Since the method now returns early when 
    # ip_address is None, the problematic line should never be reached.
    
    config_flow = EssConfigFlow()
    config_flow.hass = Mock(spec=HomeAssistant)
    
    discovery_info = ZeroconfServiceInfo(
        ip_address=IPv6Address("2001:db8::1"),
        ip_addresses=[IPv6Address("2001:db8::1")],
        port=443,
        hostname="test-device.local.",
        type="_lg-ess._tcp.local.",
        name="test-device._lg-ess._tcp.local.",
        properties={}
    )
    
    # This should not raise AttributeError anymore
    result = await config_flow.async_step_zeroconf(discovery_info)
    
    # Should abort gracefully without AttributeError
    assert result["type"] == "abort"
    assert result["reason"] == "no_ipv4_address"