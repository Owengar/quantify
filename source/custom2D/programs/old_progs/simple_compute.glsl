#version 460


layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;




uniform int split_max;
uniform vec2 data_viewport;
uniform vec2 data_viewport_start;
uniform vec2 camera_viewport;

float shortest = (int(camera_viewport.x > camera_viewport.y) * camera_viewport.y) + (int(camera_viewport.y > camera_viewport.x) * camera_viewport.x);



uniform vec2 camera_viewport_start;


vec2 camera_viewport_inverse = 1.0/camera_viewport;
vec2 margin = vec2(data_viewport * 0.15);
vec2 twox_margin = margin*2;

const vec2 V2_ONE_nONE = vec2(1, -1);
const vec2 V2_ZERO_ONE = vec2(0, 1);




layout(binding = 1, rgba8) uniform image2D image;
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


    for (int i=0; i < abs(pixeled_difference.x); i++)
    {

        imageStore(image, ivec2((i*sign(difference.x))+pixeled_pos_1.x, int((i*sign(difference.x))*slope)+pixeled_pos_1.y), vec4(1.0, 0.0, 0.0, 1.0));
    }

    for (int i=0; i < abs(pixeled_difference.y); i++)
    {

        imageStore(image, ivec2(int((i*sign(difference.y))*inverse_slope)+pixeled_pos_1.x, (i*sign(difference.y))+pixeled_pos_1.y), vec4(0.0, 1.0, 0.0, 1.0));
    }
}

void surrounding_store(ivec2 pixel_pos, vec4 color)
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

    uint split_invocation = (split_max * (gl_GlobalInvocationID.y-1)) + gl_GlobalInvocationID.x;
    split_invocation = gl_GlobalInvocationID.x;

    vec2 data_point = data[split_invocation]; //the actual data point

    
    vec2 data_point_location_normalized = (V2_ONE_nONE*(data_point-data_viewport_start + margin)/(data_viewport + twox_margin)+V2_ZERO_ONE - camera_viewport_start)*camera_viewport_inverse; //between 0.0 and 1.0 for positioning
    vec2 data_point_position_pixelized = data_point_location_normalized * image_size;
    ivec2 data_point_position_pixelized_fixed = ivec2(data_point_position_pixelized);





    









    //imageStore(image, data_point_position_pixelized_fixed, data_point_not_nan_color);
    surrounding_store(data_point_position_pixelized_fixed, vec4(1.0));
    //surrounding_store(data_point_position_pixelized_fixed, shortest, vec4(vec3(100.0/float(data_split)), 1.0));

    /*

    vec2 last_data_point = data[gl_GlobalInvocationID.x-1]; //the actual data point
    vec2 last_data_point_location_normalized = (V2_ONE_nONE*(last_data_point-data_viewport_start + margin)/(data_viewport + twox_margin)+V2_ZERO_ONE - camera_viewport_start)*camera_viewport_inverse; //between 0.0 and 1.0 for positioning
    vec2 last_data_point_position_pixelized = last_data_point_location_normalized * image_size;

    ivec2 last_data_point_position_pixelized_fixed = ivec2(last_data_point_position_pixelized);







    int cross_line_preventer = int(!(mod(double(gl_GlobalInvocationID.x), double(data_split)) < 1.0));

    //draw_line(last_data_point_location_normalized, data_point_location_normalized, image_size * int(gl_GlobalInvocationID.x-1 < data_fill) * int(!isnan(data_point.y)) * cross_line_preventer); //multiply by greater than data fill to avoid cross-screen lines at the first point that isn't filled

    */
}