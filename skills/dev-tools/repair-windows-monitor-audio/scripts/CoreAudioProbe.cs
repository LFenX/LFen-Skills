using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Threading;
using System.IO;

namespace AudioProbe {
[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")] class DeviceEnumeratorClass {}
[ComImport, Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IDevices {
 [PreserveSig] int EnumAudioEndpoints(int flow, uint mask, out ICollection collection);
 [PreserveSig] int GetDefaultAudioEndpoint(int flow, int role, out IDevice device);
 [PreserveSig] int GetDevice([MarshalAs(UnmanagedType.LPWStr)] string id, out IDevice device);
 [PreserveSig] int RegisterEndpointNotificationCallback(IntPtr callback);
 [PreserveSig] int UnregisterEndpointNotificationCallback(IntPtr callback);
}
[ComImport, Guid("0BD7A1BE-7A1A-44DB-8397-CC5392387B5E"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface ICollection {
 [PreserveSig] int GetCount(out uint count);
 [PreserveSig] int Item(uint index, out IDevice device);
}
[ComImport, Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IDevice {
 [PreserveSig] int Activate(ref Guid iid, uint clsctx, IntPtr parameters, [MarshalAs(UnmanagedType.IUnknown)] out object obj);
 [PreserveSig] int OpenPropertyStore(uint access, out IProperties store);
 [PreserveSig] int GetId([MarshalAs(UnmanagedType.LPWStr)] out string id);
 [PreserveSig] int GetState(out uint state);
}
[StructLayout(LayoutKind.Sequential)] struct PropertyKey { public Guid fmtid; public uint pid; public PropertyKey(string guid,uint p){fmtid=new Guid(guid);pid=p;} }
[StructLayout(LayoutKind.Explicit, Size=24)] struct PropVariant { [FieldOffset(0)] public ushort type; [FieldOffset(8)] public IntPtr pointer; }
[ComImport, Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IProperties {
 [PreserveSig] int GetCount(out uint count);
 [PreserveSig] int GetAt(uint index,out PropertyKey key);
 [PreserveSig] int GetValue(ref PropertyKey key,out PropVariant value);
 [PreserveSig] int SetValue(ref PropertyKey key,ref PropVariant value);
 [PreserveSig] int Commit();
}
[ComImport, Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IVolume {
 [PreserveSig] int RegisterControlChangeNotify(IntPtr p);
 [PreserveSig] int UnregisterControlChangeNotify(IntPtr p);
 [PreserveSig] int GetChannelCount(out uint n);
 [PreserveSig] int SetMasterVolumeLevel(float v,ref Guid c);
 [PreserveSig] int SetMasterVolumeLevelScalar(float v,ref Guid c);
 [PreserveSig] int GetMasterVolumeLevel(out float v);
 [PreserveSig] int GetMasterVolumeLevelScalar(out float v);
 [PreserveSig] int SetChannelVolumeLevel(uint n,float v,ref Guid c);
 [PreserveSig] int SetChannelVolumeLevelScalar(uint n,float v,ref Guid c);
 [PreserveSig] int GetChannelVolumeLevel(uint n,out float v);
 [PreserveSig] int GetChannelVolumeLevelScalar(uint n,out float v);
 [PreserveSig] int SetMute([MarshalAs(UnmanagedType.Bool)] bool mute,ref Guid c);
 [PreserveSig] int GetMute([MarshalAs(UnmanagedType.Bool)] out bool mute);
 [PreserveSig] int GetVolumeStepInfo(out uint step,out uint count);
 [PreserveSig] int VolumeStepUp(ref Guid c);
 [PreserveSig] int VolumeStepDown(ref Guid c);
 [PreserveSig] int QueryHardwareSupport(out uint mask);
 [PreserveSig] int GetVolumeRange(out float min,out float max,out float increment);
}
[ComImport, Guid("C02216F6-8C67-4B5B-9D00-D008E73E0064"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IMeter {
 [PreserveSig] int GetPeakValue(out float value);
 [PreserveSig] int GetMeteringChannelCount(out uint count);
 [PreserveSig] int GetChannelsPeakValues(uint count,[Out,MarshalAs(UnmanagedType.LPArray,SizeParamIndex=0)] float[] values);
 [PreserveSig] int QueryHardwareSupport(out uint mask);
}
[ComImport, Guid("1CB9AD4C-DBFA-4C32-B178-C2F568A703B2"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IClient {
 [PreserveSig] int Initialize(int mode,uint flags,long duration,long periodicity,IntPtr format,IntPtr session);
 [PreserveSig] int GetBufferSize(out uint frames);
 [PreserveSig] int GetStreamLatency(out long latency);
 [PreserveSig] int GetCurrentPadding(out uint frames);
 [PreserveSig] int IsFormatSupported(int mode,IntPtr format,out IntPtr closest);
 [PreserveSig] int GetMixFormat(out IntPtr format);
 [PreserveSig] int GetDevicePeriod(out long normal,out long minimum);
 [PreserveSig] int Start();
 [PreserveSig] int Stop();
 [PreserveSig] int Reset();
 [PreserveSig] int SetEventHandle(IntPtr handle);
 [PreserveSig] int GetService(ref Guid iid,[MarshalAs(UnmanagedType.IUnknown)] out object obj);
}
[ComImport, Guid("F294ACFC-3146-4483-A7BF-ADDCA7C260E2"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IRender {
 [PreserveSig] int GetBuffer(uint frames,out IntPtr data);
 [PreserveSig] int ReleaseBuffer(uint frames,uint flags);
}
[ComImport, Guid("CD63314F-3FBA-4A1B-812C-EF96358728E7"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)] interface IClock {
 [PreserveSig] int GetFrequency(out ulong frequency);
 [PreserveSig] int GetPosition(out ulong position,out ulong qpc);
 [PreserveSig] int GetCharacteristics(out uint c);
}
public class ClockResult { public string EndpointId; public int SampleRate; public int Channels; public int Bits; public uint BufferFrames; public ulong Frequency; public ulong FirstPosition; public ulong LastPosition; public double ElapsedAudioSeconds; public int AdvancingSamples; public int Samples; public string Error; }
public class EndpointInfo { public string Id; public string Name; public uint State; public string Defaults; public float Volume; public bool Muted; public float Peak; public string Error; }
public class ToneResult { public string EndpointId; public float MaxPeak; public int NonzeroSamples; public int SampleCount; public string Error; }
public static class Probe {
 [DllImport("winmm.dll", SetLastError=true)] static extern bool PlaySound(IntPtr data, IntPtr module, uint flags);
 [DllImport("ole32.dll")] static extern int PropVariantClear(ref PropVariant variant);
 static void Check(int hr){Marshal.ThrowExceptionForHR(hr);}
 static IDevices Devices(){return (IDevices)new DeviceEnumeratorClass();}
 static T Activate<T>(IDevice device){object obj;Guid id=typeof(T).GUID;Check(device.Activate(ref id,23,IntPtr.Zero,out obj));return (T)obj;}
 public static ClockResult MeasureClock(){
  var result=new ClockResult();IDevices en=Devices();IDevice d=null;IClient client=null;IRender render=null;IClock clock=null;IntPtr format=IntPtr.Zero;
  try{Check(en.GetDefaultAudioEndpoint(0,1,out d));d.GetId(out result.EndpointId);client=Activate<IClient>(d);Check(client.GetMixFormat(out format));result.Channels=Marshal.ReadInt16(format,2);result.SampleRate=Marshal.ReadInt32(format,4);result.Bits=Marshal.ReadInt16(format,14);
   Check(client.Initialize(0,0,2000000,0,format,IntPtr.Zero));Check(client.GetBufferSize(out result.BufferFrames));object obj;Guid id=typeof(IRender).GUID;Check(client.GetService(ref id,out obj));render=(IRender)obj;id=typeof(IClock).GUID;Check(client.GetService(ref id,out obj));clock=(IClock)obj;Check(clock.GetFrequency(out result.Frequency));
   IntPtr data;Check(render.GetBuffer(result.BufferFrames,out data));Check(render.ReleaseBuffer(result.BufferFrames,2));Check(client.Start());ulong qpc;Check(clock.GetPosition(out result.FirstPosition,out qpc));ulong previous=result.FirstPosition;
   for(int i=0;i<50;i++){Thread.Sleep(40);ulong pos;Check(clock.GetPosition(out pos,out qpc));if(pos>previous)result.AdvancingSamples++;result.Samples++;previous=pos;result.LastPosition=pos;uint padding;Check(client.GetCurrentPadding(out padding));uint available=result.BufferFrames-padding;if(available>0){Check(render.GetBuffer(available,out data));Check(render.ReleaseBuffer(available,2));}}
   result.ElapsedAudioSeconds=(double)(result.LastPosition-result.FirstPosition)/result.Frequency;Check(client.Stop());
  }catch(Exception e){result.Error=e.GetType().Name+": "+e.Message+" (0x"+e.HResult.ToString("X8")+")";}
  finally{if(client!=null)client.Stop();if(clock!=null)Marshal.ReleaseComObject(clock);if(render!=null)Marshal.ReleaseComObject(render);if(client!=null)Marshal.ReleaseComObject(client);if(format!=IntPtr.Zero)Marshal.FreeCoTaskMem(format);if(d!=null)Marshal.ReleaseComObject(d);Marshal.ReleaseComObject(en);}return result;
 }
 public static EndpointInfo[] Snapshot(){
  IDevices en=Devices(); var defaults=new Dictionary<string,string>();
  for(int role=0;role<3;role++){ IDevice d; if(en.GetDefaultAudioEndpoint(0,role,out d)==0){string id;d.GetId(out id);defaults[id]=(defaults.ContainsKey(id)?defaults[id]+",":"")+new[]{"Console","Multimedia","Communications"}[role];Marshal.ReleaseComObject(d);} }
  ICollection coll;Check(en.EnumAudioEndpoints(0,15,out coll));uint count;Check(coll.GetCount(out count));var result=new List<EndpointInfo>();
  for(uint i=0;i<count;i++){IDevice d;Check(coll.Item(i,out d));var r=new EndpointInfo(); d.GetId(out r.Id);d.GetState(out r.State);r.Defaults=defaults.ContainsKey(r.Id)?defaults[r.Id]:"";
   try{IProperties props;Check(d.OpenPropertyStore(0,out props));var key=new PropertyKey("A45C254E-DF1C-4EFD-8020-67D146A850E0",14);PropVariant v;Check(props.GetValue(ref key,out v));r.Name=v.type==31?Marshal.PtrToStringUni(v.pointer):"";PropVariantClear(ref v);Marshal.ReleaseComObject(props);
    if(r.State==1){var vol=Activate<IVolume>(d);Check(vol.GetMasterVolumeLevelScalar(out r.Volume));Check(vol.GetMute(out r.Muted));Marshal.ReleaseComObject(vol);var meter=Activate<IMeter>(d);Check(meter.GetPeakValue(out r.Peak));Marshal.ReleaseComObject(meter);}
   }catch(Exception e){r.Error=e.GetType().Name+": "+e.Message+" (0x"+e.HResult.ToString("X8")+")";}
   result.Add(r);Marshal.ReleaseComObject(d);
  }
  Marshal.ReleaseComObject(coll);Marshal.ReleaseComObject(en);return result.ToArray();
 }
 public static ToneResult PlayAndMeasure(){
  var result=new ToneResult();IDevices en=Devices();IDevice d;Check(en.GetDefaultAudioEndpoint(0,1,out d));d.GetId(out result.EndpointId);var meter=Activate<IMeter>(d);
  try {
   const int rate=48000; const int seconds=3; const int channels=2;const int size=rate*seconds*channels*2;
   using(var stream=new MemoryStream()){
    var w=new BinaryWriter(stream);w.Write(System.Text.Encoding.ASCII.GetBytes("RIFF"));w.Write(36+size);w.Write(System.Text.Encoding.ASCII.GetBytes("WAVEfmt "));w.Write(16);w.Write((short)1);w.Write((short)channels);w.Write(rate);w.Write(rate*channels*2);w.Write((short)(channels*2));w.Write((short)16);w.Write(System.Text.Encoding.ASCII.GetBytes("data"));w.Write(size);
    for(int n=0;n<rate*seconds;n++){double t=(double)n/rate;double local=t%1.5;double envelope=local<1.0?Math.Min(1,local/0.02)*Math.Min(1,(1-local)/0.02):0;short sample=(short)(Math.Sin(2*Math.PI*(t<1.5?440:660)*t)*2200*envelope);w.Write(sample);w.Write(sample);}w.Flush();stream.Position=0;
    var pinned=GCHandle.Alloc(stream.ToArray(),GCHandleType.Pinned);try{if(!PlaySound(pinned.AddrOfPinnedObject(),IntPtr.Zero,7))throw new Exception("PlaySound rejected test playback");for(int i=0;i<90;i++){float v;Check(meter.GetPeakValue(out v));result.MaxPeak=Math.Max(result.MaxPeak,v);if(v>0.0001f)result.NonzeroSamples++;result.SampleCount++;Thread.Sleep(40);}}finally{PlaySound(IntPtr.Zero,IntPtr.Zero,0);pinned.Free();}
   }
  }catch(Exception e){result.Error=e.GetType().Name+": "+e.Message+" (0x"+e.HResult.ToString("X8")+")";}
  finally{Marshal.ReleaseComObject(meter);Marshal.ReleaseComObject(d);Marshal.ReleaseComObject(en);}return result;
 }
}
}
