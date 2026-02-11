# MNAV Macropad Software

**Status** 
- Date: 2/10/26
- Most Recent updates: [
    Hardware <--> Software Serial Communication,
    Full Base-level Functionality, 
    Pico GPx pin to UI element Mapping, 
    Rotary Encoder Suport,
    UI to Hardware Com8 bridge establishment through fluid cron checks 
] 


**Phase:** UI Distilation to 80% completion  
**Purpose:** This repository powers the MNAV macropad — a custom Raspberry Pi Pico–based macro controller with GUI configuration.


## Structure
- src/gui/: PyQt6-based configuration interface  
- src/firmware/: Pico serial communication and flashing logic  
- src/utils/: Logging, configuration helpers, and shared utilities  
- config/: JSON configuration for device and app settings  
- 	ests/: Automated test scripts

## Ref 
- .\MNAV\Scripts\activate


## Next Steps
1. UI declutter & simplification
2. Central UI State Model (ui_state.py)
3. Actions registry (context menus & shared commands)
4. KPI Refinement 
5. Macro Palette polish 
6. HUD Framework ( Reflection based NOT a Parallel system )

