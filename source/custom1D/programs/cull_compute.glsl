#version 460


layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;




uniform int split_max;
uniform vec2 data_viewport;
uniform vec2 data_viewport_start;
uniform vec2 camera_viewport;
uniform vec2 image_size;

float shortest = (int(camera_viewport.x > camera_viewport.y) * camera_viewport.y) + (int(camera_viewport.y > camera_viewport.x) * camera_viewport.x);



uniform vec2 camera_viewport_start;


vec2 camera_viewport_inverse = 1.0/camera_viewport;
vec2 margin = vec2(data_viewport * 0.15);
vec2 twox_margin = margin*2;

const vec2 V2_ONE_nONE = vec2(1, -1);
const vec2 V2_ZERO_ONE = vec2(0, 1);





layout(std430, binding = 4) buffer ssbo
{
    vec2 data[];
};
int data_len = data.length();

layout(std430, binding = 5) buffer ssbo_out
{
    vec2 data_out[];
};





void main()
{

    uint split_invocation = (split_max * (gl_GlobalInvocationID.y-1)) + gl_GlobalInvocationID.x;
    split_invocation = gl_GlobalInvocationID.x;

    vec2 data_point = data[split_invocation]; //the actual data point

    bool data_point_is_nan = isnan(data_point.y);
    //NULL CULLING
    if (data_point_is_nan)
    {
        return;
    }
    
    
    vec2 data_point_location_normalized = (V2_ONE_nONE*(data_point-data_viewport_start + margin)/(data_viewport + twox_margin)+V2_ZERO_ONE - camera_viewport_start)*camera_viewport_inverse; //between 0.0 and 1.0 for positioning
    vec2 data_point_position_pixelized = data_point_location_normalized * image_size;
    ivec2 data_point_position_pixelized_fixed = ivec2(data_point_position_pixelized);



    //offscreen culling
    if (data_point_position_pixelized_fixed.x > image_size.x || data_point_position_pixelized_fixed.y > image_size.y || data_point_position_pixelized_fixed.x < 0 || data_point_position_pixelized_fixed.y < 0)
    {
        return;
    }
    











    

    vec2 last_data_point = data[split_invocation-1]; //the actual data point
    vec2 last_data_point_location_normalized = (V2_ONE_nONE*(last_data_point-data_viewport_start + margin)/(data_viewport + twox_margin)+V2_ZERO_ONE - camera_viewport_start)*camera_viewport_inverse; //between 0.0 and 1.0 for positioning
    vec2 last_data_point_position_pixelized = last_data_point_location_normalized * image_size;
    ivec2 last_data_point_position_pixelized_fixed = ivec2(last_data_point_position_pixelized);

    /*
    if (distance(last_data_point_position_pixelized_fixed, data_point_position_pixelized_fixed) < 15 && mod(data_point_position_pixelized_fixed.x, 2) != 0 && mod(data_point_position_pixelized_fixed.y, 2) != 0)
    {
        return;
    }
    */
    if (distance(last_data_point_position_pixelized_fixed, data_point_position_pixelized_fixed) < 6 && mod(split_invocation, 2) != 0)
    {
        return;
    }


    data_out[split_invocation] = data_point;
    
}