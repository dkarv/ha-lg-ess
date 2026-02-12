# General

Some unsorted thoughts how to reverse engineer the api. Replace 10.10.10.21 with your ip.

## Pages

Pages found in the Android app, and pages linked from there. All with `[+]` were not checked yet.

To view these, open e.g. view-source:https://LG.IP.ADD.RES/system/index.html in your browser, ignore certificate warning, and save the result to send it to me.

```
/system/index.html
|- /system/energyOverview.html
|- /system/morePV.html
|- /system/pcsLoad.html
|- /system/moreBattery.html
|- /system/moreGrid.html
|- /system/energy_level.html
|- /system/notice.html
|- /system/analysis_{day, week, month, year, day_battery, day_load}.html
|- /system/systemInfo.html
|- /system/setting.html
   |- /system/winterMode.html
   |- /system/heatpump.html
   |- /system/energy_device.html
      |- /system/evcharger.html
   |- /installer/statusConnection.html
      |- /installer/pvMeter.html
      |- /installer/upgrade_firmware.html
         |- /installer/firmware_login.html
      |- /installer/wiredSetting.html
   |- /developer/index.html
      |- /developer/pcsCalibration.html [+]
      |- /developer/logSet.html [+]
      |- /developer/agingTest.html [+]
      |- /developer/engineerMenu.html [+]
      |- /developer/referenceInput.html [+]
      |- /developer/pcsCertification.html [+]
      |- /developer/pcsSurge.html [+]
      |- /developer/timeSchedule.html [+]
      |- /developer/acceleratedLifeTest.html [+]
      |- /developer/pcsSettingInfo.html [+]
   |- /service/index.html
      |- /service/ledTest.html [+]
      |- /service/factoryTest.html [+]
      |- /service/emergencyCharging.html [+]
      |- /service/engineerMenu.html [+]
      |- /service/pcsInfo.html [+]
      |- /service/telstra.html [+]
      |- /service/pwInitialize.html [+]
   |- /system/openSource.html
   |- /system/openSourceEss.html
   |- /system/applicationInfo.html
```

## API calls

```
curl --insecure -v -H "Content-Type: application/json" https://10.10.10.21/v1/user/setting/login -X PUT -d '{"password": "d84fb8024046"}'
```
