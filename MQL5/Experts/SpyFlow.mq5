//+------------------------------------------------------------------+
//|                                                      SpyFlow.mq5 |
//|                                  Copyright 2025, AI Trader Pro   |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "AI Trader Pro"
#property link      "https://www.mql5.com"
#property version   "1.00"

#include <Files\FileTxt.mqh>

//--- Input Parameters
input string InpFileName = "flow_data.json"; // Output file name

//--- Global Variables
long ExtForeignVolume = 0;
long ExtInstitutionalVolume = 0;
long ExtRetailVolume = 0;
datetime ExtLastSaveTime = 0;

//--- Broker Groups (Hardcoded for simplicity, ideally loaded from config)
int ForeignBrokers[] = {16, 114, 45, 306, 23, 40, 127};
int InstitutionalBrokers[] = {85, 113, 72, 27, 39, 92, 111};
int RetailBrokers[] = {308, 386, 1982, 15, 147, 107, 1099};

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   // Enable Trade Transaction events
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   // Optional: Save final state
  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
   // Check if 1 second has passed to save file
   if(TimeCurrent() - ExtLastSaveTime >= 1)
     {
      SaveFlowData();
      ExtLastSaveTime = TimeCurrent();
     }
  }
//+------------------------------------------------------------------+
//| TradeTransaction function                                        |
//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction& trans,
                        const MqlTradeRequest& request,
                        const MqlTradeResult& result)
  {
   // We are using OnTick + CopyTicks for Market Flow (Tape Reading).
   // OnTradeTransaction only reports OUR trades, which is not enough for the dashboard.
   return;
  }

//+------------------------------------------------------------------+
//| Custom: Process Time & Sales                                     |
//+------------------------------------------------------------------+
void ProcessTimeAndSales()
{
   MqlTick ticks[];
   // Get last 100 trades. For production, you should track the last processed tick time
   // to avoid duplicates or missing trades. For this prototype, we snapshot last 100.
   int received = CopyTicks(_Symbol, ticks, COPY_TICKS_TRADE, 0, 100); 
   
   if(received > 0)
   {
      for(int i=0; i<received; i++)
      {
         // Synthetic Logic (Aggressor):
         // If Price > Last Price -> Buyer Aggressor
         // If Price < Last Price -> Seller Aggressor
         
         long vol = (long)ticks[i].volume; // Explicit cast to avoid warning
         
         if((ticks[i].flags & TICK_FLAG_BUY) == TICK_FLAG_BUY)
         {
             // Buyer Aggressor
             // Simulate attribution based on volume size
             if(vol >= 50) ExtForeignVolume += vol; // Big lots -> Foreign
             else if(vol >= 10) ExtInstitutionalVolume += vol; // Medium -> Inst
             else ExtRetailVolume += vol; // Small -> Retail
         }
         else if((ticks[i].flags & TICK_FLAG_SELL) == TICK_FLAG_SELL)
         {
             // Seller Aggressor
             if(vol >= 50) ExtForeignVolume -= vol;
             else if(vol >= 10) ExtInstitutionalVolume -= vol;
             else ExtRetailVolume -= vol;
         }
      }
   }
}

//+------------------------------------------------------------------+
//| Save Data to JSON                                                |
//+------------------------------------------------------------------+
void SaveFlowData()
  {
   // Use Time & Sales processing
   ProcessTimeAndSales();
   
   // Dynamic Filename: flow_data_WIN$N.json
   string dynamicFileName = "flow_data_" + _Symbol + ".json";
   
   int file_handle = FileOpen(dynamicFileName, FILE_WRITE|FILE_TXT|FILE_COMMON|FILE_ANSI);
   if(file_handle != INVALID_HANDLE)
     {
      string json = "{";
      json += "\"timestamp\": " + IntegerToString(TimeCurrent()) + ",";
      json += "\"symbol\": \"" + _Symbol + "\",";
      json += "\"flow\": {";
      json += "\"FOREIGN\": " + IntegerToString(ExtForeignVolume) + ",";
      json += "\"INSTITUTIONAL\": " + IntegerToString(ExtInstitutionalVolume) + ",";
      json += "\"RETAIL\": " + IntegerToString(ExtRetailVolume);
      json += "}";
      json += "}";
      
      FileWrite(file_handle, json);
      FileClose(file_handle);
     }
   else
     {
      Print("Failed to open file: ", dynamicFileName, " Error: ", GetLastError());
     }
  }
//+------------------------------------------------------------------+
