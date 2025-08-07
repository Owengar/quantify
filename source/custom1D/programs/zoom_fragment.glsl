#version 430
precision mediump float;


uniform sampler2D Texture;


in vec2 v_text; 
out vec3 f_color;








void main()
{


    /*
    float shortest;
    if (camera_viewport.x > camera_viewport.y)
    {
        shortest = camera_viewport.y;
    }
    else
    {
        shortest = camera_viewport.x;
    }
    float distance_cutoff = 0.005*shortest;




    int closeness = 0;
    vec2 fixed_v_text = v_text*vec2(1, -1) + vec2(0, 1);



    for (int i = 0; i < data_len; i++)
    {
        vec2 data_point = vec2(data[i].x, data[i].y);
        vec2 pixeled_data_point = (data_point-data_viewport_start)/data_viewport;
        

        float dist_to_data_point = distance(pixeled_data_point, fixed_v_text);


        closeness += int((dist_to_data_point < distance_cutoff));

    }


    
    f_color = vec3(data[int(v_text.x*1000)].x, 0.0, 0.0);

    if (closeness > 0)
    {
        f_color = vec3(0.1, 0.5, 0.5);
    }
    else
    {
        f_color = vec3(distance(v_text, vec2(0.5, 0.5))*10, 1.0, 1.0);
    }

    //f_color *= 0.00001;
    //f_color += vec3(v_text.y, 0.0, 0.0);
    */
    vec3 thing = texture(Texture, v_text).rgb;
    f_color = thing;

}