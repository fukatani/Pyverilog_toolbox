module TOP(CLK, RST);
  input CLK, RST;
  reg bit;
  always @(posedge CLK or negedge RST) begin
    if(RST) begin
      bit <= bit;
    end else begin
      bit <= func1(bit);
    end
  end

  function func1;
    input bit;
      case(bit)
        'h0: begin
          func1 = !bit;
        end
        default: begin
          func1 = !bit;
        end
      endcase
  endfunction
endmodule

