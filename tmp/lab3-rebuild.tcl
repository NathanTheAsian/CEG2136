package require ::quartus::project
package require ::quartus::flow
project_open {C:/Users/natha/CEG2136/labs/Lab3/Lab3} -revision Lab3
set_global_assignment -name PROJECT_OUTPUT_DIRECTORY {C:/Users/natha/CEG2136/labs/Lab3/output_files}
execute_flow -compile
project_close
