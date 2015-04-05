module TOP(CLK, RST, WRITE, READ, ADDR, WRITE_DATA, READ_DATA);
  input CLK,RST,WRITE,READ;
  input [2:0] ADDR;
  input [1:0] WRITE_DATA;
  output reg [1:0] READ_DATA;
  reg [1:0] reg0;
  reg reg1;

  always @(posedge CLK) begin
    if(RST) begin
      reg0[1:0] <= 0;
      reg1 <= 0;
    end else if(WRITE) begin
      case(ADDR)
        0:reg0[1:0] <= WRITE_DATA;
        1:reg1 <= WRITE_DATA[0];
      endcase
    end
  end

  always @* begin
    case(ADDR)
      0:READ_DATA[1:0] = reg0[1:0];
      1:READ_DATA[1:0] = {1'b0,reg1};
    endcase
  end

  //pyverilog don't supported case in function now.

  /*
  assign READ_DATA = get_read_data(ADDR,reg0,reg1);
  function [1:0] get_read_data;
    input [2:0] ADDR;
    input [1:0] reg0;
    input [1:0] reg1;

    begin
      case(ADDR)
        0:get_read_data = reg0;
        1:get_read_data = reg1;
      endcase
    end
  endfunction
  */

endmodule

