package com.example.localizator;

import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Handler;
import android.os.StrictMode;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.util.Calendar;
import java.util.Date;

import pub.devrel.easypermissions.AfterPermissionGranted;
import pub.devrel.easypermissions.EasyPermissions;

public class MainActivity extends AppCompatActivity {

    /**
     * Giving a request for ACCESS_FINE_LOCATION which is needed to search for bluetooth devices
     * Using an additional library EasyPermissions by Google
     */

    private final int REQUEST_LOCATION_PERMISSION = 1;

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        // Forward results to EasyPermissions
        EasyPermissions.onRequestPermissionsResult(requestCode, permissions, grantResults, this);
    }

    @AfterPermissionGranted(REQUEST_LOCATION_PERMISSION)
    public void requestLocationPermission() {
        String[] perms = {Manifest.permission.ACCESS_FINE_LOCATION,Manifest.permission.ACCESS_WIFI_STATE,Manifest.permission.INTERNET}; //If more permissions needed, simply add them to array
        if(EasyPermissions.hasPermissions(this, perms)) {
            Toast.makeText(this, "Permission already granted", Toast.LENGTH_SHORT).show();
        }
        else {
            EasyPermissions.requestPermissions(this, "Please grant the location permission", REQUEST_LOCATION_PERMISSION, perms);
        }
    }

    /**
     * Prepering bluetooth adapter
     */

    private final BluetoothAdapter BTAdapter = BluetoothAdapter.getDefaultAdapter();;

    BroadcastReceiver receiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            if(BluetoothDevice.ACTION_FOUND.equals(action)){//When bluetooth device found
                short rssi=intent.getShortExtra(BluetoothDevice.EXTRA_RSSI,Short.MIN_VALUE);
                System.out.print(rssi);
                String name = intent.getStringExtra(BluetoothDevice.EXTRA_NAME);
                TextView rssi_msg = (TextView) findViewById(R.id.textRSSIList);
                rssi_msg.setText(rssi_msg.getText()+name+" => "+rssi+"dBm\n");
                Date currentTime = Calendar.getInstance().getTime();

                //Sending device info via local network
                try {
                    Socket socket = new Socket("192.168.1.13",8369);
                    DataOutputStream DOS = new DataOutputStream(socket.getOutputStream());
                    DOS.writeUTF(currentTime+"="+name+"="+rssi+"dBm");
                    socket.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    };

    /**
     * Constant searching for devices (with 5s interval)
     */

    Handler mHandler = new Handler();
    final Runnable runnable = new Runnable() {
        @Override
        public void run() {
            // TODO Auto-generated method stub
            BTAdapter.startDiscovery();
            while(BTAdapter.isDiscovering()){}
            mHandler.postDelayed(this, 7000);
        }
    };

    /**
     * Main program
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        //Request permissions
        requestLocationPermission();

        //Register bluetooth receiver
        registerReceiver(receiver, new IntentFilter(BluetoothDevice.ACTION_FOUND));

        StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
        StrictMode.setThreadPolicy(policy);

        mHandler.postDelayed(runnable, 7000);

        /**
         * Buttons etc.
         */
        Button buttonRSSI = (Button) findViewById(R.id.button_RSSIstart);
        buttonRSSI.setOnClickListener(new View.OnClickListener(){
            public void onClick(View v){
                BTAdapter.startDiscovery();
            }
        });

        Button buttonSend = (Button) findViewById(R.id.buttonSend);
        buttonSend.setOnClickListener(new View.OnClickListener(){
            public void onClick(View v){
                try {
                    Socket socket = new Socket("192.168.1.13",8369);
                    DataOutputStream DOS = new DataOutputStream(socket.getOutputStream());
                    DOS.writeUTF("HELLO_WORLD");
                    socket.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        });
    }
}