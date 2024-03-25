using Plugin.BLE.Abstractions.Contracts;
using Plugin.BLE;
using Java.IO;
using Plugin.BLE.Abstractions.EventArgs;
using System.Collections.ObjectModel;
using Java.Nio.Channels;
using Android.Widget;
using Plugin.BLE.Android;

namespace BLEApp_permissions;

public partial class BluetoothDeviceListPage : ContentPage
{
    //List<DeviceItem> devices = new List<DeviceItem>();

    Plugin.BLE.Abstractions.Contracts.IAdapter adapter;

    public ObservableCollection<DeviceItem> Devices = new ObservableCollection<DeviceItem>();
    public BluetoothDeviceListPage(Plugin.BLE.Abstractions.Contracts.IAdapter _adapter)
    {
        InitializeComponent();

        // Richiama il metodo per popolare la lista dei dispositivi Bluetooth
        //PopulateBluetoothDeviceList();


        Devices = new ObservableCollection<DeviceItem>();
        DeviceListView.ItemsSource = Devices;
        startScan();
        adapter = _adapter;


    }


    private async void startScan()
    {
        CrossBluetoothLE.Current.Adapter.DeviceDiscovered += OnDeviceDiscovered;
        CrossBluetoothLE.Current.Adapter.ScanTimeout = 20000;

        await CrossBluetoothLE.Current.Adapter.StartScanningForDevicesAsync();



    }
    private void OnDeviceDiscovered(object sender, DeviceEventArgs e)
    {

        //devices.Add(new DeviceItem { Name = e.Device.Name, Id = e.Device.Id.ToString() });
        //DeviceListView.ItemsSource = devices;

       

        MainThread.BeginInvokeOnMainThread(() =>
        {
            Devices.Add(new DeviceItem
            {
                Id = e.Device.Id.ToString(),
                Name = e.Device.Name,
                Address = e.Device.NativeDevice.ToString()
            }); 

            ;
        });
    }


    private void DeviceListView_ItemTapped(object sender, ItemTappedEventArgs e)
    {
        // Recupera il dispositivo selezionato dalla ListView
        var selectedDevice = e.Item as DeviceItem;



        // Connessione al dispositivo selezionato
        // Qui dovresti implementare la logica per la connessione al dispositivo
        // Ad esempio, navigare alla pagina di connessione passando il dispositivo selezionato come parametro
        Navigation.PushAsync(new MainPage( selectedDevice ));
    }


}

public class DeviceItem
{
    public string Id { get; set; }
    public string Name { get; set; }
    public string Address { get; set; }
}