
from typing import Optional
from bluesky_nexus.models.nx_core_models import (
    BaseModel,
    Field,
    ConfigDict,
    NXattrModel,
    NXgroupModel,
    NXfieldModelForAttribute,
    NXfieldModelWithPrePostRunString
)
from bluesky_nexus.models.nx_detector_channel_model import NXdetector_channelModel
from bluesky_nexus.models.nx_data_model import NXdataModel
from bluesky_nexus.models.nx_note_model import NXnoteModel
from bluesky_nexus.models.nx_collection_model import NXcollectionModel
from bluesky_nexus.models.nx_detector_module_model import NXdetector_moduleModel
from bluesky_nexus.models.nx_transformations_model import NXtransformationsModel

class NXdetectorModel(NXgroupModel):

    default: NXattrModel = Field(NXattrModel(value="data"), description='Default')

    # ----- time_of_flight -----
    class time_of_flightModel(NXfieldModelWithPrePostRunString):
        class AttributesModel(BaseModel):
            axis: Optional[NXfieldModelForAttribute] = Field(None, gt=0, description="Obligatory value: 3")
            primary: Optional[NXfieldModelForAttribute] = Field(None, gt=0, description="Obligatory value: 1")
            long_name: Optional[NXfieldModelForAttribute] = Field(None, description="Total time of flight")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to the 'time_of_flight' field.")

    time_of_flight: Optional[time_of_flightModel]= Field(None, description="Total time of flight")

    # ----- raw_time_of_flight -----
    class raw_time_of_flightModel(NXfieldModelWithPrePostRunString):
        class AttributesModel(BaseModel):
            frequency: Optional[NXfieldModelForAttribute] = Field(None, description="Clock frequency in Hz")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to the 'raw_time_of_flight' field.")

    raw_time_of_flight: Optional[raw_time_of_flightModel]= Field(None, description="In DAQ clock pulses")
    detector_number: Optional[int]= Field(None, description="Identifier for detector (pixels) Can be multidimensional, if needed")
    
    # ----- data -----
    class dataModel(NXfieldModelWithPrePostRunString):
        class AttributesModel(BaseModel):
            long_name: Optional[NXfieldModelForAttribute] = Field(None, gt=0, description="Title of measurement")
            check_sum: Optional[NXfieldModelForAttribute] = Field(None, description="Integral of data as check of data integrity")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to the 'data' field.")

    data: Optional[dataModel]= Field(None, description="Data values from the detector. The rank and dimension ordering should follow a principle of slowest to fastest measurement axes and may be explicitly specified in application definitions.")
    data_errors: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="The best estimate of the uncertainty in the data value (array size should match the data field). Where possible, this should be the standard deviation, which has the same units as the data.")

    # ----- x_pixel_offset -----
    class x_pixel_offsetModel(NXfieldModelWithPrePostRunString):
        class AttributesModel(BaseModel):
            axis: Optional[NXfieldModelForAttribute] = Field(None, gt=0, description="Obligatory value: 1")
            primary: Optional[NXfieldModelForAttribute] = Field(None, gt=0, description="Obligatory value: 1")
            long_name: Optional[NXfieldModelForAttribute] = Field(None, description="x-axis offset from detector center")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to the 'x_pixel_offset' field.")

    x_pixel_offset: Optional[x_pixel_offsetModel]= Field(None, description="Offset from the detector center in x-direction. Can be multidimensional when needed.")

    # ----- y_pixel_offset -----
    class y_pixel_offsetModel(NXfieldModelWithPrePostRunString):

        class AttributesModel(BaseModel):
            axis: Optional[NXfieldModelForAttribute] = Field(None, gt=0, description="Obligatory value: 1")
            primary: Optional[NXfieldModelForAttribute] = Field(None, gt=0, description="Obligatory value: 1")
            long_name: Optional[NXfieldModelForAttribute] = Field(None, description="y-axis offset from detector center")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to the 'y_pixel_offset' field.")

    y_pixel_offset: Optional[y_pixel_offsetModel]= Field(None, description="Offset from the detector center in y-direction. Can be multidimensional when needed.")    

    # ----- z_pixel_offset -----
    class z_pixel_offsetModel(NXfieldModelWithPrePostRunString):
        class AttributesModel(BaseModel):
            axis: Optional[NXfieldModelForAttribute] = Field(None, gt=0, description="Obligatory value: 1")
            primary: Optional[NXfieldModelForAttribute] = Field(None, gt=0, description="Obligatory value: 1")
            long_name: Optional[NXfieldModelForAttribute] = Field(None, description="z-axis offset from detector center")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to the 'z_pixel_offset' field.")

    z_pixel_offset: Optional[z_pixel_offsetModel]= Field(None, description="Offset from the detector center in z-direction. Can be multidimensional when needed.")    
    
    distance: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="This is the distance to the previous component in the instrument; most often the sample. The usage depends on the nature of the detector: Most often it is the distance of the detector assembly. But there are irregular detectors. In this case the distance must be specified for each detector pixel.")
    polar_angle: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="This is the polar angle of the detector towards the previous component in the instrument; most often the sample. The usage depends on the nature of the detector. Most often it is the polar_angle of the detector assembly. But there are irregular detectors. In this case, the polar_angle must be specified for each detector pixel.")
    azimuthal_angle: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="This is the azimuthal angle angle of the detector towards the previous component in the instrument; most often the sample. The usage depends on the nature of the detector. Most often it is the azimuthal_angle of the detector assembly. But there are irregular detectors. In this case, the azimuthal_angle must be specified for each detector pixel.")
    description: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="name/manufacturer/model/etc. information")
    serial_number: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Serial number for the detector")
    local_name: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Local name for the detector")
    solid_angle: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Solid angle subtended by the detector at the sample")
    x_pixel_size: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Size of each detector pixel. If it is scalar all pixels are the same size.")
    y_pixel_size: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Size of each detector pixel. If it is scalar all pixels are the same size")
    dead_time: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Detector dead time")
    gas_pressure: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Detector gas pressure")
    detection_gas_path: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="maximum drift space dimension")
    
    # ----- crate -----
    class crateModel(NXfieldModelWithPrePostRunString):
        class AttributesModel(BaseModel):
            local_name: Optional[NXfieldModelForAttribute] = Field(None, description="Equivalent local term")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to the 'crate' field.")
    crate: Optional[crateModel]= Field(None, description="Crate number of detector")    

    # ----- slot -----
    class slotModel(NXfieldModelWithPrePostRunString):
        class AttributesModel(BaseModel):
            local_name: Optional[NXfieldModelForAttribute] = Field(None, description="Equivalent local term")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to the 'slot' field.")
    slot: Optional[slotModel]= Field(None, description="Slot number of detector")   

    # ----- input -----
    class inputModel(NXfieldModelWithPrePostRunString):
        class AttributesModel(BaseModel):
            local_name: Optional[NXfieldModelForAttribute] = Field(None, description="Equivalent local term")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to the 'input' field.")
    input: Optional[inputModel]= Field(None, description="Input number of detector")   
    
    type: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Description of type such as He3 gas cylinder, He3 PSD, scintillator, fission chamber, proportion counter, ion chamber, ccd, pixel, image plate, CMOS, …")
    real_time: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Real-time of the exposure (use this if exposure time varies for each array element, otherwise use count_time field).")
    
    # ----- start_time -----
    class start_timeModel(NXfieldModelWithPrePostRunString):
        class AttributesModel(BaseModel):
            start: Optional[NXfieldModelForAttribute] = Field(None, description="absolute reference")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to the 'start_time' field.")
    start_time: Optional[start_timeModel]= Field(None, description="start time for each frame, with the start attribute as absolute reference")   

    # ----- stop_time -----
    class stop_timeModel(NXfieldModelWithPrePostRunString):
        class AttributesModel(BaseModel):
            start: Optional[NXfieldModelForAttribute] = Field(None, description="absolute reference")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to the 'stop_time' field.")
    stop_time: Optional[stop_timeModel]= Field(None, description="stop time for each frame, with the start attribute as absolute reference")
    
    calibration_date: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="date of last calibration (geometry and/or efficiency) measurements")
    layout: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="How the detector is represented, any of these values: point | linear | area")
    count_time: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Elapsed actual counting time")
    sequence_number: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="In order to properly sort the order of the images taken in (for example) a tomography experiment, a sequence number is stored with each image.")
    beam_center_x: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="This is the x position where the direct beam would hit the detector. This is a length and can be outside of the actual detector. The length can be in physical units or pixels as documented by the units attribute.")
    beam_center_y: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="This is the y position where the direct beam would hit the detector. This is a length and can be outside of the actual detector. The length can be in physical units or pixels as documented by the units attribute.")
    frame_start_number: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="This is the start number of the first frame of a scan. In protein crystallography measurements one often scans a couple of frames on a give sample, then does something else, then returns to the same sample and scans some more frames. Each time with a new data file. This number helps concatenating such measurements.")
    diameter: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="The diameter of a cylindrical detector")
    acquisition_mode: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="The acquisition mode of the detector. Any of these values: gated, triggered, summed, event, histogrammed, decimated")
    angular_calibration_applied: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="True when the angular calibration has been applied in the electronics, false otherwise.")
    angular_calibration: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Angular calibration data.")
    flatfield_applied: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="True when the flat field correction has been applied in the electronics, false otherwise.")    
    flatfield: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Flat field correction data.")    
    flatfield_errors: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Errors of the flat field correction data. The form flatfield_error is deprecated.")    
    pixel_mask_applied: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="True when the pixel mask correction has been applied in the electronics, false otherwise.")
    pixel_mask: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="The 32-bit pixel mask for the detector. Can be either one mask for the whole dataset (i.e. an array with indices i, j) or each frame can have its own mask (in which case it would be an array with indices np, i, j).") 
    image_key: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="This field allow to distinguish different types of exposure to the same detector “data” field. Some techniques require frequent (re-)calibration inbetween measuremnts and this way of recording the different measurements preserves the chronological order with is important for correct processing.") 
    countrate_correction_applied: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Counting detectors usually are not able to measure all incoming particles, especially at higher count-rates. Count-rate correction is applied to account for these errors.") 
    countrate_correction_lookup_table: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="The countrate_correction_lookup_table defines the LUT used for count-rate correction. It maps a measured count to its corrected value.") 
    virtual_pixel_interpolation_applied: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="True when virtual pixel interpolation has been applied, false otherwise.") 
    bit_depth_readout: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="How many bits the electronics reads per pixel. With CCD’s and single photon counting detectors, this must not align with traditional integer sizes. This can be 4, 8, 12, 14, 16, …") 
    detector_readout_time: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Time it takes to read the detector (typically milliseconds). This is important to know for time resolved experiments.") 
    trigger_delay_time: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Time it takes to start exposure after a trigger signal has been received. This is the reaction time of the detector firmware after receiving the trigger signal to when the detector starts to acquire the exposure, including any user set delay.. This is important to know for time resolved experiments.") 
    trigger_delay_time_set: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="User-specified trigger delay.")
    trigger_internal_delay_time: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Time it takes to start exposure after a trigger signal has been received. This is the reaction time of the detector hardware after receiving the trigger signal to when the detector starts to acquire the exposure. It forms the lower boundary of the trigger_delay_time when the user does not request an additional delay.") 
    trigger_dead_time: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Time during which no new trigger signal can be accepted. Typically this is the trigger_delay_time + exposure_time + readout_time. This is important to know for time resolved experiments.") 
    frame_time: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="This is time for each frame. This is exposure_time + readout time.") 
    gain_setting: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="The gain setting of the detector. This is a detector-specific value meant to document the gain setting of the detector during data collection, for detectors with multiple available gain settings.") 
    saturation_value: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="The value at which the detector goes into saturation. Especially common to CCD detectors, the data is known to be invalid above this value.") 
    underload_value: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="The lowest value at which pixels for this detector would be reasonably measured. The data is known to be invalid below this value.") 
    number_of_cycles: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="CCD images are sometimes constructed by summing together multiple short exposures in the electronics. This reduces background etc. This is the number of short exposures used to sum images for an image.") 
    sensor_material: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="At times, radiation is not directly sensed by the detector. Rather, the detector might sense the output from some converter like a scintillator. This is the name of this converter material.") 
    sensor_thickness: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="At times, radiation is not directly sensed by the detector. Rather, the detector might sense the output from some converter like a scintillator. This is the thickness of this converter material.") 
    threshold_energy: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="Single photon counter detectors can be adjusted for a certain energy range in which they work optimally. This is the energy setting for this.") 
    depends_on: Optional[NXfieldModelWithPrePostRunString]= Field(None, description="NeXus positions components by applying a set of translations and rotations to apply to the component starting from 0, 0, 0. ")
    CHANNELNAME_channel: Optional[NXdetector_channelModel]= Field(None, description="Group containing the description and metadata for a single channel from a multi-channel detector.")
    
    # ----- efficiency -----
    class efficiencyModel(NXdataModel):
        class AttributesModel(NXdataModel.AttributesModel):
            signal: Optional[NXfieldModelForAttribute] = Field(None, description="Obligatory value: efficiency")
            axes: Optional[NXfieldModelForAttribute] = Field(None, description="Any of these values: . | . . | . . . | . . . . | wavelength")
            wavelength_indices: Optional[NXfieldModelForAttribute] = Field(None, description="Obligatory value: 0")
            model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
        attributes: Optional[AttributesModel] = Field(None, description="Attributes specific to the efficiency field.")
    efficiency: Optional[efficiencyModel]= Field(None, description="Spectral efficiency of detector with respect to e.g. wavelength")
    
    calibration_method: Optional[NXnoteModel]= Field(None, description="summary of conversion of array data to pixels (e.g. polynomial approximations) and location of details of the calibrations")
    data_file: Optional[NXnoteModel]= Field(None, description="data_file")
    COLLECTION: Optional[NXcollectionModel]= Field(None, description="Use this group to provide other data related to this NXdetector group.")
    DETECTOR_MODULE: Optional[NXdetector_moduleModel]= Field(None, description="For use in special cases where the data in NXdetector is represented in several parts, each with a separate geometry.")
    TRANSFORMATIONS: Optional[NXtransformationsModel]= Field(None, description="This is the group recommended for holding the chain of translation and rotation operations necessary to position the component within the instrument. The dependency chain may however traverse similar groups in other component groups.")   
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
