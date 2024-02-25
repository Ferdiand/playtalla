#include "HAL.h"

void HAL::HAL_Init()
{
    Buzz_init();
    Audio_Init();
    GPS_Init();
    esp_init();
}

void HAL::HAL_Update()
{
    IMU_Update();
    MAG_Update();
    Audio_Update();
    esp_update();
}
