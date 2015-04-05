module TOP(CLK, RST, WRITE, READ, ADDR, WRITE_DATA, READ_DATA);
  input CLK,RST,WRITE,READ;
  input [2:0] ADDR;
  input [1:0] WRITE_DATA;
  output reg [1:0] READ_DATA;
  reg [4:3] reg0;


  always @(posedge CLK) begin
    if(RST) begin
      reg0[4:3] <= 0;
    end else if(WRITE) begin
      case(ADDR)
        0:reg0[4:3] <= WRITE_DATA[1:0];
      endcase
    end
  end

  always @* begin
    case(ADDR)
      0:READ_DATA[1:0] = reg0[4:3];
    endcase
  end



endmodule

