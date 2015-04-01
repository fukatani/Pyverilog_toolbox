module TOP(CLK, RST, WRITE, READ, ADDR, WRITE_DATA, READ_DATA);
  input CLK,RST,WRITE,READ;
  input [2:0] ADDR;
  input [3:0] WRITE_DATA;
  output [3:0] READ_DATA;

  reg [1:0] reg1,reg0;

  always @(posedge CLK) begin
    if(RST) begin
      reg0[1:0] <= 0;
      reg1[1:0] <= 0;
    end else if(WRITE) begin
      case(ADDR)
        1:{reg1[1:0], reg0[1:0]} <= WRITE_DATA[3:0];
      endcase
    end
  end

  always @* begin
    case(ADDR)
      1:READ_DATA[3:0] = {reg1[1:0], reg0[1:0]};
    endcase
  end
endmodule

