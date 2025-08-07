#version 460


layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;





uniform vec2 data_viewport;
uniform vec2 data_viewport_start;
uniform vec2 camera_viewport;




uniform vec2 camera_viewport_start;


vec2 camera_viewport_inverse = 1.0/camera_viewport;
vec2 margin = vec2(data_viewport * 0.15);
vec2 twox_margin = margin*2;

const vec2 V2_ONE_nONE = vec2(1, -1);
const vec2 V2_ZERO_ONE = vec2(0, 1);




layout(binding = 1, rgba32f) uniform image2D image;
ivec2 image_size = imageSize(image);


layout(std430, binding = 4) buffer ssbo
{
    vec2 data[];
};
int data_len = data.length();





void draw_line(vec2 norm_pos_1, vec2 norm_pos_2, ivec2 im_size)
{
    vec2 difference = (norm_pos_2-norm_pos_1);

    ivec2 pixeled_pos_1 = ivec2(im_size * norm_pos_1);
    ivec2 pixeled_pos_2 = ivec2(im_size * norm_pos_2);

    ivec2 pixeled_difference = pixeled_pos_2-pixeled_pos_1;

    float slope = difference.y/difference.x;
    float inverse_slope = 1.0/slope;


    uint i = uint((float(gl_GlobalInvocationID.y)/50.0)*pixeled_difference.x);
    imageStore(image, ivec2((i*sign(difference.x))+pixeled_pos_1.x, int((i*sign(difference.x))*slope)+pixeled_pos_1.y), vec4(1.0, 0.0, 0.0, 1.0));
    //i = uint((gl_GlobalInvocationID.y/100)*pixeled_difference.y);
    //imageStore(image, ivec2(int((i*sign(difference.y))*inverse_slope)+pixeled_pos_1.x, (i*sign(difference.y))+pixeled_pos_1.y), vec4(0.0, 1.0, 0.0, 1.0));

}


void draw_linebad(vec2 norm_pos_1, vec2 norm_pos_2, ivec2 im_size)
{
    vec2 difference = (norm_pos_2-norm_pos_1);

    ivec2 pixeled_pos_1 = ivec2(im_size * norm_pos_1);
    ivec2 pixeled_pos_2 = ivec2(im_size * norm_pos_2);

    ivec2 pixeled_difference = pixeled_pos_2-pixeled_pos_1;

    float slope = difference.y/difference.x;
    float inverse_slope = 1.0/slope;


    for (int i=0; i < abs(pixeled_difference.x); i++)
    {

        imageStore(image, ivec2((i*sign(difference.x))+pixeled_pos_1.x, int((i*sign(difference.x))*slope)+pixeled_pos_1.y), vec4(1.0, 0.0, 0.0, 1.0));
    }

    for (int i=0; i < abs(pixeled_difference.y); i++)
    {

        imageStore(image, ivec2(int((i*sign(difference.y))*inverse_slope)+pixeled_pos_1.x, (i*sign(difference.y))+pixeled_pos_1.y), vec4(0.0, 1.0, 0.0, 1.0));
    }
}

void surrounding_store(ivec2 pixel_pos, float shortest, vec4 color)
{

    // Center of the circle
    imageStore(image, pixel_pos + ivec2(0, 0), color);

    // Radius 1
    imageStore(image, pixel_pos + ivec2(1, 0), color);
    imageStore(image, pixel_pos + ivec2(-1, 0), color);
    imageStore(image, pixel_pos + ivec2(0, 1), color);
    imageStore(image, pixel_pos + ivec2(0, -1), color);

    // Radius 2
    imageStore(image, pixel_pos + ivec2(2, 0), color);
    imageStore(image, pixel_pos + ivec2(-2, 0), color);
    imageStore(image, pixel_pos + ivec2(0, 2), color);
    imageStore(image, pixel_pos + ivec2(0, -2), color);
    imageStore(image, pixel_pos + ivec2(1, 1), color);
    imageStore(image, pixel_pos + ivec2(-1, 1), color);
    imageStore(image, pixel_pos + ivec2(1, -1), color);
    imageStore(image, pixel_pos + ivec2(-1, -1), color);

    // Radius 3
    imageStore(image, pixel_pos + ivec2(3, 0), color);
    imageStore(image, pixel_pos + ivec2(-3, 0), color);
    imageStore(image, pixel_pos + ivec2(0, 3), color);
    imageStore(image, pixel_pos + ivec2(0, -3), color);
    imageStore(image, pixel_pos + ivec2(2, 1), color);
    imageStore(image, pixel_pos + ivec2(2, -1), color);
    imageStore(image, pixel_pos + ivec2(-2, 1), color);
    imageStore(image, pixel_pos + ivec2(-2, -1), color);
    imageStore(image, pixel_pos + ivec2(1, 2), color);
    imageStore(image, pixel_pos + ivec2(-1, 2), color);
    imageStore(image, pixel_pos + ivec2(1, -2), color);
    imageStore(image, pixel_pos + ivec2(-1, -2), color);

    // Radius 4
    imageStore(image, pixel_pos + ivec2(4, 0), color);
    imageStore(image, pixel_pos + ivec2(-4, 0), color);
    imageStore(image, pixel_pos + ivec2(0, 4), color);
    imageStore(image, pixel_pos + ivec2(0, -4), color);
    imageStore(image, pixel_pos + ivec2(3, 1), color);
    imageStore(image, pixel_pos + ivec2(3, -1), color);
    imageStore(image, pixel_pos + ivec2(-3, 1), color);
    imageStore(image, pixel_pos + ivec2(-3, -1), color);
    imageStore(image, pixel_pos + ivec2(1, 3), color);
    imageStore(image, pixel_pos + ivec2(-1, 3), color);
    imageStore(image, pixel_pos + ivec2(1, -3), color);
    imageStore(image, pixel_pos + ivec2(-1, -3), color);
    imageStore(image, pixel_pos + ivec2(2, 2), color);
    imageStore(image, pixel_pos + ivec2(2, -2), color);
    imageStore(image, pixel_pos + ivec2(-2, 2), color);
    imageStore(image, pixel_pos + ivec2(-2, -2), color);
        


}





void main()
{

    

    vec2 data_point = data[gl_GlobalInvocationID.x]; //the actual data point


    //NULL CULLING
    /*
    if (data_point_is_nan)
    {
        return;
    }
    */
    
    vec2 data_point_location_normalized = (V2_ONE_nONE*(data_point-data_viewport_start + margin)/(data_viewport + twox_margin)+V2_ZERO_ONE - camera_viewport_start)*camera_viewport_inverse; //between 0.0 and 1.0 for positioning
    vec2 data_point_position_pixelized = data_point_location_normalized * image_size;
    ivec2 data_point_position_pixelized_fixed = ivec2(data_point_position_pixelized);

    bool current_dp_offscreen = (data_point_position_pixelized_fixed.x > image_size.x || data_point_position_pixelized_fixed.y > image_size.y || data_point_position_pixelized_fixed.x < 0 || data_point_position_pixelized_fixed.y < 0);









    vec2 last_data_point = data[gl_GlobalInvocationID.x-1]; //the actual data point
    vec2 last_data_point_location_normalized = (V2_ONE_nONE*(last_data_point-data_viewport_start + margin)/(data_viewport + twox_margin)+V2_ZERO_ONE - camera_viewport_start)*camera_viewport_inverse; //between 0.0 and 1.0 for positioning
    vec2 last_data_point_position_pixelized = last_data_point_location_normalized * image_size;
    ivec2 last_data_point_position_pixelized_fixed = ivec2(last_data_point_position_pixelized);

    bool last_dp_offscreen = (last_data_point_position_pixelized_fixed.x > image_size.x || last_data_point_position_pixelized_fixed.y > image_size.y || last_data_point_position_pixelized_fixed.x < 0 || last_data_point_position_pixelized_fixed.y < 0);

    if (last_dp_offscreen && current_dp_offscreen)
    {
        return;
    }





    draw_line(last_data_point_location_normalized, data_point_location_normalized, image_size * int(!isnan(data_point.y))); //multiply by greater than data fill to avoid cross-screen lines at the first point that isn't filled


}