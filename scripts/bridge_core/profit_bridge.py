"""
Profit Pro RTD Bridge
=====================
Reads real-time data from Profit Pro Excel RTD and provides a clean Python interface.

Author: AI Trader Pro
Date: 2025-12-06
"""

import win32com.client
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("Bridge.ProfitRTD")


class ProfitBridge:
    """
    Bridge to read RTD data from Profit Pro Excel workbook.
    
    Connects to an already-open Excel file and reads specific cells
    containing real-time market data, indicators, and scores.
    
    Uses win32com instead of xlwings for better COM reliability.
    """
    
    def __init__(self, workbook_name: str = "profit-data.xlsx"):
        """
        Initialize connection to Excel workbook.
        
        Args:
            workbook_name: Name of the Excel file (must be already open)
        """
        self.workbook_name = workbook_name
        self.excel = None
        self.wb = None
        self.sheet = None
        self._connect()
    
    def _connect(self):
        """Connect to the active Excel workbook using win32com."""
        try:
            # Method 1: Try GetObject (existing instance)
            try:
                self.excel = win32com.client.GetObject(None, "Excel.Application")
                logger.debug("Connected via GetObject")
            except:
                # Method 2: Try Dispatch (may create new instance or connect to existing)
                self.excel = win32com.client.Dispatch("Excel.Application")
                logger.debug("Connected via Dispatch")
            
            # Check if any workbooks are open
            if self.excel.Workbooks.Count == 0:
                raise Exception("No workbooks open in Excel. Please open a file.")
            
            # Find workbook by name
            for wb in self.excel.Workbooks:
                if self.workbook_name in wb.Name:
                    self.wb = wb
                    break
            
            if not self.wb:
                # If not found by exact name, use first workbook
                self.wb = self.excel.Workbooks(1)
                logger.warning(f"⚠️ '{self.workbook_name}' not found, using: {self.wb.Name}")
            
            # Get "Dados" sheet or first sheet
            try:
                self.sheet = self.wb.Worksheets("Dados")
            except:
                try:
                    self.sheet = self.wb.Worksheets(1)
                    sheet_name = str(self.sheet.Name) if hasattr(self.sheet, 'Name') else "Sheet1"
                    logger.warning(f"⚠️ Sheet 'Dados' not found, using first sheet")
                except Exception as e:
                    logger.error(f"Error accessing worksheet: {e}")
                    self.sheet = self.wb.Worksheets(1)
            
            wb_name = str(self.wb.Name) if hasattr(self.wb, 'Name') else "Unknown"
            logger.info(f"✅ Connected to Excel: {wb_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Excel: {e}")
            logger.info("💡 Dica: Certifique-se que:")
            logger.info("   1. Excel está aberto")
            logger.info("   2. Algum arquivo .xlsx está aberto")
            raise
    
    def _safe_read(self, cell: str, default: Any = None) -> Any:
        """
        Safely read a cell value, handling errors and None values.
        
        Args:
            cell: Cell address (e.g., "B2")
            default: Default value if cell is empty or error
            
        Returns:
            Cell value or default
        """
        try:
            value = self.sheet.Range(cell).Value
            
            # Handle Excel errors (#N/A, #VALUE!, etc.)
            if value is None or (isinstance(value, str) and value.startswith("#")):
                return default
            
            # Try to convert to float if it's a number
            if isinstance(value, (int, float)):
                return float(value)
            
            # Handle string numbers (e.g., "1.234,56" or "1,234.56")
            if isinstance(value, str):
                # Remove thousand separators and convert decimal comma to dot
                cleaned = value.replace(".", "").replace(",", ".")
                try:
                    return float(cleaned)
                except ValueError:
                    return value  # Return as string if not a number
            
            return value
        except Exception as e:
            logger.warning(f"⚠️ Error reading cell {cell}: {e}")
            return default
    
    def get_data(self) -> Dict[str, Any]:
        """
        Read all RTD data from Excel and return structured dictionary.
        
        Returns:
            Dictionary with keys: 'win', 'wdo', 'macro', 'timestamp'
        """
        try:
            # WIN (Mini Índice) - Row 2
            win_data = {
                "symbol": "WIN",
                "price": self._safe_read("B2", 0.0),
                "bear_power": self._safe_read("G2", 0.0),
                "bull_power": self._safe_read("H2", 0.0),
                "hilo_activator": self._safe_read("I2", 0.0),
                "rsi": self._safe_read("J2", 50.0),
                "flow": self._safe_read("L2", 0.0),
                "vwap": self._safe_read("M2", 0.0),
                "score": self._safe_read("Q2", 0.0),
                "decision": self._safe_read("R2", "AGUARDAR")
            }
            
            # WDO (Mini Dólar) - Row 3
            wdo_data = {
                "symbol": "WDO",
                "price": self._safe_read("B3", 0.0),
                "bear_power": self._safe_read("G3", 0.0),
                "bull_power": self._safe_read("H3", 0.0),
                "hilo_activator": self._safe_read("I3", 0.0),
                "rsi": self._safe_read("J3", 50.0),
                "flow": self._safe_read("L3", 0.0),
                "vwap": self._safe_read("M3", 0.0),
                "score": self._safe_read("Q3", 0.0),
                "decision": self._safe_read("R3", "AGUARDAR")
            }
            
            # Macro Context
            macro_data = {
                "di_var": self._safe_read("E17", 0.0),
                "sp500_var": self._safe_read("E16", 0.0)
            }
            
            return {
                "win": win_data,
                "wdo": wdo_data,
                "macro": macro_data,
                "timestamp": self._safe_read("A1", "")  # Assuming timestamp in A1
            }
        
        except Exception as e:
            logger.error(f"❌ Error reading data: {e}")
            return {
                "win": {},
                "wdo": {},
                "macro": {},
                "timestamp": None
            }
    
    def close(self):
        """Close connection (optional, Excel stays open)."""
        logger.info("🔌 Disconnecting from Excel")
        # Note: We don't close the workbook as it should stay open for RTD


# Test/Demo
if __name__ == "__main__":
    import time
    import json
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print("=" * 60)
    print("Profit Pro RTD Bridge - Test Mode")
    print("=" * 60)
    print("\nMake sure Excel is OPEN with any .xlsx file!")
    print("Press Ctrl+C to stop\n")
    
    try:
        # Initialize bridge
        bridge = ProfitBridge("profit-data.xlsx")
        
        # Read data in loop
        while True:
            data = bridge.get_data()
            
            # Pretty print
            print("\n" + "=" * 60)
            print(f"Timestamp: {data.get('timestamp', 'N/A')}")
            print("-" * 60)
            
            # WIN
            win = data.get("win", {})
            print(f"\n📊 WIN (Mini Índice)")
            print(f"   Preço: {win.get('price', 0):.2f}")
            print(f"   Bull Power: {win.get('bull_power', 0):.1f} | Bear Power: {win.get('bear_power', 0):.1f}")
            print(f"   RSI: {win.get('rsi', 0):.1f} | VWAP: {win.get('vwap', 0):.2f}")
            print(f"   Fluxo: {win.get('flow', 0):.0f}")
            print(f"   Score: {win.get('score', 0):.1f} | Decisão: {win.get('decision', 'N/A')}")
            
            # WDO
            wdo = data.get("wdo", {})
            print(f"\n💵 WDO (Mini Dólar)")
            print(f"   Preço: {wdo.get('price', 0):.2f}")
            print(f"   Bull Power: {wdo.get('bull_power', 0):.1f} | Bear Power: {wdo.get('bear_power', 0):.1f}")
            print(f"   RSI: {wdo.get('rsi', 0):.1f} | VWAP: {wdo.get('vwap', 0):.2f}")
            print(f"   Fluxo: {wdo.get('flow', 0):.0f}")
            print(f"   Score: {wdo.get('score', 0):.1f} | Decisão: {wdo.get('decision', 'N/A')}")
            
            # Macro
            macro = data.get("macro", {})
            print(f"\n🌍 Macro")
            print(f"   DI Var: {macro.get('di_var', 0):.2f}%")
            print(f"   S&P 500 Var: {macro.get('sp500_var', 0):.2f}%")
            
            # Wait 1 second
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n👋 Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
